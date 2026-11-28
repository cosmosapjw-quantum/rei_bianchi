#pragma once
// Exact reference for conditional finite-model diagnostics. Not a physical rate provider.
#include <boost/multiprecision/cpp_int.hpp>
#include <algorithm>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
namespace c3a {
using R = boost::multiprecision::cpp_rational;
struct Error : std::runtime_error { using std::runtime_error::runtime_error; };
struct C {
    R re=0, im=0;
    C()=default;
    C(int a):re(a){}
    C(R a):re(std::move(a)){}
    C(R a,R b):re(std::move(a)),im(std::move(b)){}
};
inline C operator+(const C&a,const C&b){return {a.re+b.re,a.im+b.im};}
inline C operator-(const C&a,const C&b){return {a.re-b.re,a.im-b.im};}
inline C operator-(const C&a){return {-a.re,-a.im};}
inline C operator*(const C&a,const C&b){return {a.re*b.re-a.im*b.im,a.re*b.im+a.im*b.re};}
inline C conj(const C&a){return {a.re,-a.im};}
inline R abs2(const C&a){return a.re*a.re+a.im*a.im;}
inline bool operator==(const C&a,const C&b){return a.re==b.re&&a.im==b.im;}
inline bool operator!=(const C&a,const C&b){return !(a==b);}
inline C operator/(const C&a,const C&b){R d=abs2(b);if(d==0)throw Error("DIVISION_BY_ZERO");C n=a*conj(b);return {n.re/d,n.im/d};}
struct Mat {
    std::size_t nr,nc;
    std::vector<C> a;
    static std::size_t count(std::size_t r,std::size_t c){if(r==0||c==0||r>64||c>64)throw Error("DIMENSION_BOUND");return r*c;}
    Mat(std::size_t r,std::size_t c):nr(r),nc(c),a(count(r,c)){}
    std::size_t index(std::size_t i,std::size_t j)const{if(i>=nr||j>=nc)throw Error("INDEX_OUT_OF_RANGE");return i*nc+j;}
    C& operator()(std::size_t i,std::size_t j){return a.at(index(i,j));}
    const C& operator()(std::size_t i,std::size_t j)const{return a.at(index(i,j));}
};
inline Mat eye(std::size_t n){Mat x(n,n);for(std::size_t i=0;i<n;++i)x(i,i)=1;return x;}
inline Mat adj(const Mat&x){Mat a(x.nc,x.nr);for(std::size_t i=0;i<x.nr;++i)for(std::size_t j=0;j<x.nc;++j)a(j,i)=conj(x(i,j));return a;}
inline Mat operator+(const Mat&a,const Mat&b){if(a.nr!=b.nr||a.nc!=b.nc)throw Error("DIMENSION_MISMATCH");Mat x(a.nr,a.nc);for(std::size_t i=0;i<x.a.size();++i)x.a[i]=a.a[i]+b.a[i];return x;}
inline Mat operator-(const Mat&a,const Mat&b){if(a.nr!=b.nr||a.nc!=b.nc)throw Error("DIMENSION_MISMATCH");Mat x(a.nr,a.nc);for(std::size_t i=0;i<x.a.size();++i)x.a[i]=a.a[i]-b.a[i];return x;}
inline Mat operator*(const Mat&a,const Mat&b){if(a.nc!=b.nr)throw Error("DIMENSION_MISMATCH");Mat x(a.nr,b.nc);for(std::size_t i=0;i<a.nr;++i)for(std::size_t k=0;k<a.nc;++k){if(a(i,k)==C(0))continue;for(std::size_t j=0;j<b.nc;++j)x(i,j)=x(i,j)+a(i,k)*b(k,j);}return x;}
inline bool operator==(const Mat&a,const Mat&b){return a.nr==b.nr&&a.nc==b.nc&&a.a==b.a;}
inline bool zero(const Mat&a){return std::all_of(a.a.begin(),a.a.end(),[](const C&z){return z==C(0);});}
inline bool hermitian(const Mat&a){return a.nr==a.nc&&a==adj(a);}
inline void require_hpd(const Mat&a){
    if(!hermitian(a))throw Error("METRIC_NOT_HERMITIAN");
    Mat t=a;
    for(std::size_t k=0;k<a.nr;++k){
        C d=t(k,k);if(d.im!=0||d.re<=0)throw Error("METRIC_NOT_POSITIVE_DEFINITE");
        for(std::size_t i=k+1;i<a.nr;++i)for(std::size_t j=k+1;j<a.nr;++j)t(i,j)=t(i,j)-t(i,k)*t(k,j)/d;
    }
}
inline Mat solve(Mat a,Mat b){
    if(a.nr!=a.nc||a.nr!=b.nr)throw Error("SOLVE_DIMENSION");
    const auto n=a.nr;
    for(std::size_t k=0;k<n;++k){
        std::size_t pivot=k;while(pivot<n&&a(pivot,k)==C(0))++pivot;
        if(pivot==n)throw Error("SINGULAR_NO_PSEUDOINVERSE");
        if(pivot!=k){for(std::size_t j=0;j<n;++j)std::swap(a(k,j),a(pivot,j));for(std::size_t j=0;j<b.nc;++j)std::swap(b(k,j),b(pivot,j));}
        C d=a(k,k);for(std::size_t j=k;j<n;++j)a(k,j)=a(k,j)/d;for(std::size_t j=0;j<b.nc;++j)b(k,j)=b(k,j)/d;
        for(std::size_t i=0;i<n;++i)if(i!=k){C f=a(i,k);for(std::size_t j=k;j<n;++j)a(i,j)=a(i,j)-f*a(k,j);for(std::size_t j=0;j<b.nc;++j)b(i,j)=b(i,j)-f*b(k,j);}
    }return b;
}
inline C quadratic(const Mat&c,const Mat&a){if(c.nc!=1||c.nr!=a.nr||a.nr!=a.nc)throw Error("STATE_DIMENSION");return (adj(c)*a*c)(0,0);}
inline Mat columns(std::size_t n,const std::vector<std::size_t>&ids){Mat z(n,ids.size());std::vector<bool>seen(n,false);for(std::size_t k=0;k<ids.size();++k){if(ids[k]>=n||seen[ids[k]])throw Error("BAD_CHANNEL_SELECTION");seen[ids[k]]=true;z(ids[k],k)=1;}return z;}
struct Projection {Mat coefficient,covariant;};
inline Projection project(const Mat&o,const Mat&z){
    require_hpd(o);
    if(z.nr!=o.nr)throw Error("CHANNEL_DIMENSION");
    Mat g=adj(z)*o*z;
    require_hpd(g);
    Mat p=z*solve(g,adj(z)*o);
    return {p,o*p};
}
inline void require_psd(const Mat&a){
    if(!hermitian(a))throw Error("EFFECT_NOT_HERMITIAN");
    Mat t=a;
    for(std::size_t k=0;k<a.nr;++k){
        C d=t(k,k);if(d.im!=0||d.re<0)throw Error("EFFECT_NOT_POSITIVE");
        if(d.re==0){for(std::size_t i=k+1;i<a.nr;++i)if(t(i,k)!=C(0))throw Error("ZERO_PIVOT_NONZERO_COUPLING");continue;}
        for(std::size_t i=k+1;i<a.nr;++i)for(std::size_t j=k+1;j<a.nr;++j)t(i,j)=t(i,j)-t(i,k)*t(k,j)/d;
    }
}
inline R probability(const Mat&o,const Mat&k,const Mat&c){require_hpd(o);require_psd(k);require_psd(o-k);C n=quadratic(c,o),q=quadratic(c,k);if(n.im!=0||n.re<=0)throw Error("ZERO_OR_INVALID_NORM");if(q.im!=0)throw Error("NONREAL_EXPECTATION");return q.re/n.re;}
struct Effect {Mat metric,covariant,op;bool is_projector,subspace_preserved;};
inline Effect compress(const Mat&o,const Projection&p,const Mat&q){
    require_hpd(o);
    if(p.coefficient.nr!=o.nr||p.coefficient.nc!=o.nr||q.nr!=o.nr)throw Error("COMPRESSION_DIMENSION");
    if(!(p.covariant==o*p.coefficient)||!(p.coefficient*p.coefficient==p.coefficient)||!(adj(p.coefficient)*o==p.covariant))throw Error("INVALID_INPUT_PROJECTOR");
    Mat m=adj(q)*o*q;require_hpd(m);
    Mat e=adj(q)*p.covariant*q;Mat d=solve(m,e);
    bool invariant=(p.coefficient*q==q*d);
    bool idempotent=(d*d==d);
    if(invariant!=idempotent)throw Error("COMPRESSION_IDENTITY_FAILURE");
    return {m,e,d,idempotent,invariant};
}
inline void require_partition(const Mat&o,const std::vector<Mat>&zs,bool complete){
    require_hpd(o);if(zs.empty())throw Error("EMPTY_PARTITION");Mat k(o.nr,o.nr);
    for(std::size_t i=0;i<zs.size();++i){auto p=project(o,zs[i]);k=k+p.covariant;
        for(std::size_t j=0;j<i;++j)if(!zero(adj(zs[i])*o*zs[j]))throw Error("OVERLAPPING_SUBSPACES_NOT_EXCLUSIVE");
    }
    if(complete&&!(k==o))throw Error("PARTITION_INCOMPLETE");
}
} // namespace c3a
