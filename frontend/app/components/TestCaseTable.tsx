"use client";

import React, { useEffect, useState } from "react";
import { AgGridReact } from "ag-grid-react";
import { ColDef } from "ag-grid-community";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";

interface TestCase {
  id: number;
  input: string;
  output: string;
  is_correct: boolean;
  reason: string;
}

const TestCaseTable: React.FC = () => {
  const [rowData, setRowData] = useState<TestCase[]>([]);

  useEffect(() => {
    fetch("http://localhost:9000/input-output")
      .then((response) => response.json())
      .then((data: TestCase[]) => setRowData(data))
      .catch((error) => {
        console.error("Failed to fetch test cases:", error);
        // Optionally, you can set an error state here to display to the user
        // setError("Failed to load test cases. Please try again later.");
      });
  }, []);

  const columnDefs: ColDef[] = [
    { headerName: "ID", field: "id" },
    { headerName: "Input", field: "input" },
    { headerName: "Output", field: "output" },
    { headerName: "Is Correct", field: "is_correct" },
    { headerName: "Reason", field: "reason" },
  ];

  return (
    <div className="ag-theme-alpine" style={{ height: 400, width: "100%" }}>
      <AgGridReact<TestCase>
        rowData={rowData}
        columnDefs={columnDefs}
        pagination={true}
        paginationPageSize={10}
      />
    </div>
  );
};

export default TestCaseTable;
