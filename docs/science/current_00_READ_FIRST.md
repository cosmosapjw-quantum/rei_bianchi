# R2B upload-recovery v2

This is a reconstructed Git-delivery stage created after `part-0003` of the previous reconstructed incremental bundle failed upload-status processing and was not retained.

The R2B operator was rerun from the verified R2A base and canonical locked inputs. The regenerated logical outputs are not byte-identical to the previous gzip streams, so they have new SHA-256 values and new Git commit identities. Independent all-row validation and 16 tests pass. This delivery reconstruction does not change the R2B scientific verdict or authorize production node chemistry.
