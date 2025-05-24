<!DOCTYPE html>
<html>
<head>
    <title>Invoice Reconciliation</title>
    <style>
        /* Basic styling for the reconciliation table */
        table {
            width: 80%;
            border-collapse: collapse;
            margin: 30px auto;
        }
        th, td {
            padding: 12px;
            border: 1px solid #ccc;
            text-align: center;
        }
        th {
            background-color: #2e3b4e;
            color: white;
        }
        .matched {
            background-color: #d4edda; /* Light green for matched rows */
        }
        .unmatched {
            background-color: #f8d7da; /* Light red for unmatched rows */
        }
    </style>
</head>
<body>
    <h2 style="text-align:center;">Invoice Reconciliation Results</h2>

    <?php
        // Define the API URL (FastAPI backend)
        $api_url = "http://localhost:8000/reconcile";

        // Initialize cURL request
        $curl = curl_init($api_url);
        curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);

        // Execute the request and store the response
        $response = curl_exec($curl);

        // If the request fails, show the error
        if ($response === false) {
            echo "<p style='text-align:center;'>Error fetching data: " . curl_error($curl) . "</p>";
        } else {
            // Decode the JSON response
            $data = json_decode($response, true);

            // Check if reconciliation data is available
            if (!empty($data['reconciliation'])) {
                echo "<table>";
                echo "<tr><th>Invoice No</th><th>Vendor</th><th>Amount</th><th>Status</th><th>PO No</th></tr>";

                // Display each row in the HTML table
                foreach ($data['reconciliation'] as $item) {
                    $class = strtolower($item['status']); 
                    echo "<tr class='{$class}'>";
                    echo "<td>{$item['invoice_number']}</td>";
                    echo "<td>{$item['vendor']}</td>";
                    echo "<td>{$item['amount']}</td>";
                    echo "<td>{$item['status']}</td>";
                    echo "<td>" . ($item['po_number'] ?? '—') . "</td>";
                    echo "</tr>";
                }

                echo "</table>";
            } else {
                // If no data returned
                echo "<p style='text-align:center;'>No data found.</p>";
            }
        }

        // Close the cURL session
        curl_close($curl);
    ?>
</body>
</html>
