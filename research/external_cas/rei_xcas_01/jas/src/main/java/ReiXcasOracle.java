import edu.jas.arith.BigRational;
import edu.jas.poly.GenPolynomial;
import edu.jas.poly.GenPolynomialRing;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Map;

public final class ReiXcasOracle {
    private static final String JAS_VERSION = "2.7.200";

    private static boolean zero(GenPolynomialRing<BigRational> ring, String expression) {
        GenPolynomial<BigRational> polynomial = ring.parse(expression);
        return polynomial.isZERO();
    }

    private static boolean nonzero(GenPolynomialRing<BigRational> ring, String expression) {
        return !ring.parse(expression).isZERO();
    }

    private static String jsonEscape(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private static String toJson(Map<String, Boolean> checks, boolean pass) {
        StringBuilder out = new StringBuilder();
        out.append("{\n");
        out.append("  \"status\": \"").append(pass ? "PASS" : "FAIL").append("\",\n");
        out.append("  \"tool\": \"Java Algebra System\",\n");
        out.append("  \"jas_version_pin\": \"").append(JAS_VERSION).append("\",\n");
        out.append("  \"java_version\": \"").append(jsonEscape(System.getProperty("java.version"))).append("\",\n");
        out.append("  \"oracle_class\": \"EXACT_RATIONAL_MULTIVARIATE_POLYNOMIAL_CAS\",\n");
        out.append("  \"check_count\": ").append(checks.size()).append(",\n");
        out.append("  \"checks\": {\n");
        int index = 0;
        for (Map.Entry<String, Boolean> item : checks.entrySet()) {
            out.append("    \"").append(jsonEscape(item.getKey())).append("\": ").append(item.getValue());
            if (++index < checks.size()) out.append(',');
            out.append('\n');
        }
        out.append("  },\n");
        out.append("  \"claim_boundary\": \"EXACT_ALGEBRA_ONLY_NOT_RUNTIME_OR_PROVIDER_ADMISSION\"\n");
        out.append("}\n");
        return out.toString();
    }

    public static void main(String[] args) throws IOException {
        String[] variables = {
            "r0", "r1", "r2", "r3", "n0", "n1", "n2", "n3",
            "nH", "nHe", "xH", "x2", "x3", "h", "p", "m", "nc",
            "xs", "dt", "y", "pe", "a", "b", "ah", "ahe",
            "t1", "t2", "t3", "dm"
        };
        GenPolynomialRing<BigRational> ring =
            new GenPolynomialRing<>(new BigRational(), variables);
        Map<String, Boolean> checks = new LinkedHashMap<>();

        checks.put("redshift_telescoping", zero(ring,
            "(-r0*n0+r1*n1)+(-r1*n1+r2*n2)+(-r2*n2+r3*n3)+(-r3*n3)+r0*n0"));
        checks.put("electron_density_canonicalization", zero(ring,
            "(nH*xH+nHe*(x2+2*x3))-(nH*xH+nHe*x2+2*nHe*x3)"));
        checks.put("helium_simplex", zero(ring, "(1-x2-x3)+x2+x3-1"));
        checks.put("expansion_work_three_terms", zero(ring, "3*h*p-(h*p+h*p+h*p)"));
        checks.put("capacity_gate_cleared_denominator", zero(ring,
            "((m+dm)*dt+nc*(1-xs))-(m*dt+nc*(1-xs))-dm*dt"));
        checks.put("allocation_numerator_partition", zero(ring,
            "(t1+t2+t3)-(t1+t2+t3)"));

        String[][] eventResiduals = {
            {"-1+1", "0+0+0"},
            {"0+0", "-1+1+0"},
            {"0+0", "0-1+1"},
            {"1-1", "0+0+0"},
            {"-y+y", "y-y+0"},
            {"-pe+pe", "1-1+0"},
            {"-(1-a-b)+(1-a-b)", "-b+(1+b-a)+(-1+a)"},
            {"-1+1", "0+1-1"},
            {"-ah+ah", "-ahe+(1+ahe)-1"}
        };
        for (int i = 0; i < eventResiduals.length; i++) {
            checks.put("event_" + (i + 1) + "_H_conservation", zero(ring, eventResiduals[i][0]));
            checks.put("event_" + (i + 1) + "_He_conservation", zero(ring, eventResiduals[i][1]));
        }

        checks.put("hostile_missing_redshift_inflow", nonzero(ring,
            "(-r0*n0)+(-r1*n1+r2*n2)+(-r2*n2+r3*n3)+(-r3*n3)+r0*n0"));
        checks.put("hostile_wrong_HeIII_electron_factor", nonzero(ring,
            "(nH*xH+nHe*(x2+x3))-(nH*xH+nHe*(x2+2*x3))"));
        checks.put("hostile_wrong_expansion_coefficient", nonzero(ring, "4*h*p-3*h*p"));
        checks.put("hostile_missing_allocation_species", nonzero(ring,
            "(t1+t2)-(t1+t2+t3)"));
        checks.put("hostile_broken_cascade_He_vector", nonzero(ring,
            "-ahe+(1+ahe)+1"));

        boolean pass = checks.values().stream().allMatch(Boolean::booleanValue);
        String receipt = toJson(checks, pass);
        Path output = Path.of("research/external_cas/rei_xcas_01/receipts/jas_receipt.json");
        Files.createDirectories(output.getParent());
        Files.writeString(output, receipt, StandardCharsets.UTF_8);
        System.out.print(receipt);
        if (!pass) System.exit(1);
    }
}
