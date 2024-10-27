"use client";

import React, { useState, useEffect } from "react";
import {
  Drawer,
  Button,
  TextField,
  FormControl,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormLabel,
  IconButton,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";

interface TestCase {
  id: number;
  input: string;
  output: string;
  is_correct: boolean;
  reason: string;
}

const TestCaseTable: React.FC = () => {
  const [rowData, setRowData] = useState<TestCase[]>([]);
  const [selectedTestCase, setSelectedTestCase] = useState<TestCase | null>(
    null
  );
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  useEffect(() => {
    fetch("http://localhost:9000/input-output")
      .then((response) => response.json())
      .then((data: TestCase[]) => setRowData(data))
      .catch((error) => {
        console.error("Failed to fetch test cases:", error);
      });
  }, [rowData]);

  const handleRowClick = (testCase: TestCase) => {
    setSelectedTestCase(testCase);
    setIsDrawerOpen(true);
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | { name?: string; value: unknown }>
  ) => {
    if (selectedTestCase) {
      setSelectedTestCase({
        ...selectedTestCase,
        [e.target.name as string]: e.target.value,
      });
    }
  };

  const handleSubmit = () => {
    if (selectedTestCase) {
      fetch("http://localhost:9000/testcase", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(selectedTestCase),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("Successfully submitted:", data);
          // Update the table with the new data
          setRowData((prevData) =>
            prevData.map((testCase) =>
              testCase.id === data.id ? data : testCase
            )
          );
          setIsDrawerOpen(false);
        })
        .catch((error) => {
          console.error("Failed to submit test case:", error);
        });
    }
  };

  const handleDelete = (id: number) => {
    fetch(`http://localhost:9000/testcase/${id}`, {
      method: "DELETE",
    })
      .then((response) => {
        if (response.ok) {
          // Remove the deleted test case from the state
          setRowData((prevData) =>
            prevData.filter((testCase) => testCase.id !== id)
          );
        } else {
          throw new Error("Failed to delete test case");
        }
      })
      .catch((error) => {
        console.error("Error deleting test case:", error);
      });
  };

  return (
    <div className="p-4">
      <table className="min-w-full bg-gray-100 border border-gray-300 table-fixed">
        <thead>
          <tr>
            <th
              className="py-2 px-4 border-b text-blue-800 text-left"
              style={{ width: "10%" }}
            >
              ID
            </th>
            <th
              className="py-2 px-4 border-b text-blue-800 text-left"
              style={{ width: "30%" }}
            >
              Input
            </th>
            <th
              className="py-2 px-4 border-b text-blue-800 text-left"
              style={{ width: "30%" }}
            >
              Output
            </th>
            <th
              className="py-2 px-4 border-b text-blue-800 text-left"
              style={{ width: "10%" }}
            >
              Is Correct
            </th>
            <th
              className="py-2 px-4 border-b text-blue-800 text-left"
              style={{ width: "20%" }}
            >
              Reason
            </th>
            <th
              className="py-2 px-4 border-b text-blue-800 text-left"
              style={{ width: "10%" }}
            >
              Actions
            </th>
          </tr>
        </thead>
        <tbody>
          {rowData.map((testCase) => (
            <tr
              key={testCase.id}
              className="hover:bg-gray-200 cursor-pointer"
              onClick={() => handleRowClick(testCase)}
            >
              <td
                className="py-2 px-4 border-b text-gray-900"
                style={{ width: "10%" }}
              >
                {testCase.id}
              </td>
              <td
                className="py-2 px-4 border-b text-gray-900 break-words whitespace-normal"
                style={{ width: "30%" }}
              >
                {testCase.input}
              </td>
              <td
                className="py-2 px-4 border-b text-gray-900 break-words whitespace-normal"
                style={{ width: "30%" }}
              >
                {testCase.output}
              </td>
              <td
                className="py-2 px-4 border-b text-gray-900"
                style={{ width: "10%" }}
              >
                {String(testCase.is_correct)}
              </td>
              <td
                className="py-2 px-4 border-b text-gray-900 break-words whitespace-normal"
                style={{ width: "20%" }}
              >
                {testCase.reason}
              </td>
              <td
                className="py-2 px-4 border-b text-gray-900"
                style={{ width: "10%" }}
                onClick={(e) => e.stopPropagation()} // Prevent row click when clicking the delete button
              >
                <IconButton
                  aria-label="delete"
                  onClick={() => handleDelete(testCase.id)}
                  size="small"
                  color="error"
                >
                  <DeleteIcon />
                </IconButton>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <Drawer
        anchor="right"
        open={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
      >
        <div style={{ width: 300, padding: 20 }}>
          {selectedTestCase && (
            <>
              <h2 className="text-xl font-bold mb-4">
                Edit {selectedTestCase.input}
              </h2>
              <TextField
                label="Input"
                name="input"
                value={selectedTestCase.input}
                onChange={handleInputChange}
                fullWidth
                margin="normal"
              />
              <TextField
                label="Output"
                name="output"
                value={selectedTestCase.output}
                onChange={handleInputChange}
                fullWidth
                margin="normal"
              />
              <FormControl component="fieldset" margin="normal">
                <FormLabel component="legend">Is Correct</FormLabel>
                <RadioGroup
                  name="is_correct"
                  value={String(selectedTestCase.is_correct)}
                  onChange={handleInputChange}
                  row
                >
                  <FormControlLabel
                    value="true"
                    control={<Radio />}
                    label="True"
                  />
                  <FormControlLabel
                    value="false"
                    control={<Radio />}
                    label="False"
                  />
                </RadioGroup>
              </FormControl>
              <TextField
                label="Reason"
                name="reason"
                value={selectedTestCase.reason}
                onChange={handleInputChange}
                fullWidth
                margin="normal"
              />
              <Button
                variant="contained"
                color="primary"
                onClick={handleSubmit}
              >
                Submit
              </Button>
            </>
          )}
        </div>
      </Drawer>
    </div>
  );
};

export default TestCaseTable;
