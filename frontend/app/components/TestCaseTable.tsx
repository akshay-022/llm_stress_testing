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
import DeleteIcon from "@mui/icons-material/Delete";

export interface TestCase {
  id: number;
  input: string;
  output: string;
  is_correct: boolean;
  reason: string;
}

const TestCaseTable: React.FC<{
  promptId: number;
  updateCorrectPercentage: (percentage: number) => void;
}> = ({ promptId, updateCorrectPercentage }) => {
  const [rowData, setRowData] = useState<TestCase[]>([]);
  const [selectedTestCase, setSelectedTestCase] = useState<TestCase | null>(
    null
  );
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const fetchTestCases = async () => {
    try {
      const response = await fetch(
        `http://localhost:9000/prompts/${promptId}/testcases`
      );
      const data = await response.json();
      setRowData(data.test_cases);
      updateCorrectPercentage(data.percent_correct);
    } catch (error) {
      console.error("Failed to fetch test cases:", error);
    }
  };

  useEffect(() => {
    fetchTestCases();
  }, [promptId, updateCorrectPercentage]);

  const handleRowClick = (testCase: TestCase) => {
    setSelectedTestCase(testCase);
    setIsDrawerOpen(true);
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | { name?: string; value: unknown }>
  ) => {
    if (selectedTestCase) {
      const { name, value } = e.target;
      let updatedValue = value;

      if (name === "is_correct") {
        updatedValue = value === "true";
      }

      setSelectedTestCase({
        ...selectedTestCase,
        [name as keyof TestCase]: updatedValue,
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
          fetchTestCases(); // Re-fetch test cases after successful submission
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
          fetchTestCases(); // Re-fetch test cases after successful deletion
        } else {
          throw new Error("Failed to delete test case");
        }
      })
      .catch((error) => {
        console.error("Error deleting test case:", error);
      });
  };

  return (
    <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      <table className="w-full text-gray-300">
        <thead className="bg-gray-700 text-teal-400">
          <tr>
            <th className="p-3 text-left">ID</th>
            <th className="p-3 text-left">Input</th>
            <th className="p-3 text-left">Output</th>
            <th className="p-3 text-left">Is Correct</th>
            <th className="p-3 text-left">Reason</th>
            <th className="p-3 text-left">Actions</th>
          </tr>
        </thead>
        <tbody>
          {rowData.map((testCase) => (
            <tr
              key={testCase.id}
              className="border-t border-gray-700 hover:bg-gray-750 cursor-pointer"
              onClick={() => handleRowClick(testCase)}
            >
              <td className="p-3">{testCase.id}</td>
              <td className="p-3">{testCase.input}</td>
              <td className="p-3">{testCase.output}</td>
              <td className="p-3">
                <span
                  className={`px-2 py-1 rounded ${
                    testCase.is_correct
                      ? "bg-green-800 text-green-200"
                      : "bg-red-800 text-red-200"
                  }`}
                >
                  {testCase.is_correct ? "True" : "False"}
                </span>
              </td>
              <td className="p-3">{testCase.reason}</td>
              <td className="p-3">
                <button
                  className="text-red-400 hover:text-red-300"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(testCase.id);
                  }}
                >
                  <DeleteIcon />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <Drawer
        anchor="right"
        open={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        classes={{ paper: "bg-gray-900 text-white w-full max-w-2xl" }}
      >
        <div className="p-6 h-full overflow-y-auto bg-gray-900">
          {selectedTestCase && (
            <>
              <h2 className="text-2xl font-bold mb-6 text-teal-400">
                Edit Test Case
              </h2>
              <TextField
                label="Input"
                name="input"
                value={selectedTestCase.input}
                onChange={handleInputChange}
                fullWidth
                margin="normal"
                variant="outlined"
                multiline
                rows={4}
                InputLabelProps={{ className: "text-teal-300" }}
                InputProps={{
                  className: "text-white border-gray-600 bg-gray-800",
                }}
              />
              <TextField
                label="Output"
                name="output"
                value={selectedTestCase.output}
                onChange={handleInputChange}
                fullWidth
                margin="normal"
                variant="outlined"
                multiline
                rows={4}
                InputLabelProps={{ className: "text-teal-300" }}
                InputProps={{
                  className: "text-white border-gray-600 bg-gray-800",
                }}
              />
              <FormControl component="fieldset" margin="normal">
                <FormLabel component="legend" className="text-teal-300">
                  Is Correct
                </FormLabel>
                <RadioGroup
                  name="is_correct"
                  value={String(selectedTestCase.is_correct)}
                  onChange={handleInputChange}
                  row
                >
                  <FormControlLabel
                    value="true"
                    control={<Radio className="text-teal-400" />}
                    label="True"
                    className="text-white"
                  />
                  <FormControlLabel
                    value="false"
                    control={<Radio className="text-teal-400" />}
                    label="False"
                    className="text-white"
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
                variant="outlined"
                multiline
                rows={4}
                InputLabelProps={{ className: "text-teal-300" }}
                InputProps={{
                  className: "text-white border-gray-600 bg-gray-800",
                }}
              />
              <Button
                variant="contained"
                color="primary"
                onClick={handleSubmit}
                className="mt-6 bg-teal-500 hover:bg-teal-600 text-white"
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
