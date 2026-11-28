# Source-provider input coercion clarification

The frozen provider remains byte-identical to its executed SHA256
`9d40436fbebd2e99666cf15ed069ba4041693de32da843dc23b9672d59b12a16`.

`_real` validates after NumPy array construction. Scalar Boolean and all-Boolean
arrays are rejected. Mixed Boolean/numeric sequences follow NumPy numeric
coercion before validation; the code does not recursively reject Boolean
elements after that coercion. The broad sentence “Booleans ... are rejected”
in the original provider README/docstring is read under this precise contract.
The saved24 rejection cases cover their actual inputs, not all mixed sequences.
No scientific input in the saved provider, derivation or129-temperature run
contains mixed Boolean/numeric elements. The independent review identifies
this as a documentation issue, with no kernel change or replay needed.

The source-native model, temperature domain, binary64 constants and resulting
moments are unchanged. Consumers wanting strict heterogeneous-sequence input
validation must apply that validation before array construction.
