# C3 official source register

Checked 22 November 2026. References are scoped to C3; the shared source register
and all existing Member1/Member2/Member3 A3 references are unchanged. PySpark 3.5.7
is a pinned published release used in this experiment, not a claim of the newest release.
Region: local Windows computer, no managed cloud service or preview capability used.

1. Apache Spark. *Window functions*, Spark 3.5.7. Ordered `ROW_NUMBER` supports the
   explicit first-record rule. <https://spark.apache.org/docs/3.5.7/sql-ref-syntax-qry-select-window.html>
2. Apache Spark. *RDD programming guide*, Spark 3.5.7. Partitions, lazy transformations,
   actions, shuffles, persistence and lineage. <https://spark.apache.org/docs/3.5.7/rdd-programming-guide.html>
3. Apache Spark. *Performance tuning*, Spark 3.5.7. Shuffle partitions, caching and AQE.
   <https://spark.apache.org/docs/3.5.7/sql-performance-tuning.html>
4. Zaharia, M., et al. (2012). *Resilient distributed datasets: A fault-tolerant abstraction
   for in-memory cluster computing.* NSDI '12, pp. 15-28. Primary research on reuse,
   lineage and intermediate disk costs, not a speedup measurement of this fixture.
   <https://www.usenix.org/system/files/conference/nsdi12/nsdi12-final138.pdf>
5. Apache Spark. *Cluster mode overview*, Spark 3.5.7. Driver/executor/task roles and
   distinction from single-machine local mode. <https://spark.apache.org/docs/3.5.7/cluster-overview.html>
6. Apache Spark. *Installation*, PySpark 3.5.7. Python/Java dependencies and PyPI install.
   <https://spark.apache.org/docs/3.5.7/api/python/getting_started/install.html>
7. Dean, J., & Ghemawat, S. (2004). *MapReduce: Simplified data processing on large
   clusters.* OSDI '04, pp. 137-150. Historical map/shuffle/reduce and fault-reexecution
   model. <https://research.google/pubs/mapreduce-simplified-data-processing-on-large-clusters/>
8. Eclipse Adoptium. *Temurin 17 official runtime metadata API*, Windows x64 HotSpot JRE.
   The local download was checked against the API's SHA-256 before extraction; binary
   and API metadata are local under ignored `.venv/java/`, not GitHub deliverables.
   <https://api.adoptium.net/v3/assets/latest/17/hotspot?architecture=x64&image_type=jre&os=windows&vendor=eclipse>

Runtime versions are recorded from actual execution in `summary.json`, not inferred
from documentation. No prices, cloud region, cluster availability or cloud performance
are asserted. The case workload comes from assignment Table 1; hand-trace input comes
from Table 2 on p. 9. Extended timestamps and extra records are wholly synthetic.
