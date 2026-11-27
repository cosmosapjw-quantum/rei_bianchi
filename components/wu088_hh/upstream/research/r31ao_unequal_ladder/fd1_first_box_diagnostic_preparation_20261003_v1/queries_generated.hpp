#pragma once
#define FD1_QUERY_SCOPE_SHA256 "20ff5d09ea36b1a87489ea80961bb692161ff881fa4075c71637b81afc9cfc51"
struct QuerySpec { const char* id; unsigned cell; const char* parent_raw_sha; const char* endpoints[4]; };
static const QuerySpec QUERY_SPECS[] = {
{"Q272",272,"553fb6722b002e21e1fcbd990864b4a681b21289a8b5fae09f41229409eb4d4f",{"274877906944","1099511627776","1/512","1/64"}},
{"Q000",0,"0f15f0a70417189dc7baf731db0042be01491dcbf94b10321ca70aaf1ca0fc90",{"1/512","1/64","1/512","1/64"}},
};
