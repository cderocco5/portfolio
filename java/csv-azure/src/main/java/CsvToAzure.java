import com.azure.storage.blob.*;
import com.azure.storage.blob.models.*;
import org.apache.commons.csv.*;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;

public class CsvToAzure {

    // Replace with your connection string
    private static final String AZURE_CONNECTION_STRING = "<YOUR_AZURE_STORAGE_CONNECTION_STRING>";
    private static final String CONTAINER_NAME = "csvdata";
    private static final String CSV_FILE_PATH = "data.csv";

    public static void main(String[] args) {
        try {
            // 1. Parse CSV
            Reader reader = Files.newBufferedReader(Paths.get(CSV_FILE_PATH));
            Iterable<CSVRecord> records = CSVFormat.DEFAULT
                    .withFirstRecordAsHeader()
                    .parse(reader);

            // 2. Initialize Azure Blob Container
            BlobServiceClient blobServiceClient = new BlobServiceClientBuilder()
                    .connectionString(AZURE_CONNECTION_STRING)
                    .buildClient();

            BlobContainerClient containerClient = blobServiceClient.getBlobContainerClient(CONTAINER_NAME);
            if (!containerClient.exists()) {
                containerClient.create();
            }

            // 3. Send each row to Azure Storage as individual blobs
            int counter = 1;
            for (CSVRecord record : records) {
                StringBuilder sb = new StringBuilder();
                record.toMap().forEach((k, v) -> sb.append(k).append(": ").append(v).append("\n"));

                String blobName = "row-" + counter + ".txt";
                BlobClient blobClient = containerClient.getBlobClient(blobName);

                InputStream dataStream = new ByteArrayInputStream(sb.toString().getBytes());
                blobClient.upload(dataStream, sb.toString().getBytes().length, true);

                counter++;
            }

            System.out.println("CSV data successfully uploaded to Azure Storage!");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}