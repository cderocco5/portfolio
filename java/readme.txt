# compile
mvn compile
mvn package

mvn exec:java -Dexec.mainClass="CsvToAzure"

# jar
java -cp target/your-jar-name.jar CsvToAzure