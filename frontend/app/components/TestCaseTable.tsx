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
} from "@mui/material";

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
  }, []);

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
          setIsDrawerOpen(false);
        })
        .catch((error) => {
          console.error("Failed to submit test case:", error);
        });
    }
  };

  return (
    <div className="p-4">
      <table className="min-w-full bg-gray-100 border border-gray-300">
        <thead>
          <tr>
            <th className="py-2 px-4 border-b text-blue-800 text-left">ID</th>
            <th className="py-2 px-4 border-b text-blue-800 text-left">
              Input
            </th>
            <th className="py-2 px-4 border-b text-blue-800 text-left">
              Output
            </th>
            <th className="py-2 px-4 border-b text-blue-800 text-left">
              Is Correct
            </th>
            <th className="py-2 px-4 border-b text-blue-800 text-left">
              Reason
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
              <td className="py-2 px-4 border-b text-gray-900">
                {testCase.id}
              </td>
              <td className="py-2 px-4 border-b text-gray-900">
                {testCase.input}
              </td>
              <td className="py-2 px-4 border-b text-gray-900">
                {testCase.output}
              </td>
              <td className="py-2 px-4 border-b text-gray-900">
                {String(testCase.is_correct)}
              </td>
              <td className="py-2 px-4 border-b text-gray-900">
                {testCase.reason}
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
