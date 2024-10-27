import React, { useState } from "react";
import { Button, Modal, Box, TextareaAutosize } from "@mui/material";

interface HeaderProps {
  promptId: number;
  promptName: string;
  prompt: string;
  modelName: string;
  correctPercentage: number | null;
}

const Header: React.FC<HeaderProps> = ({
  promptId,
  promptName,
  prompt,
  modelName,
  correctPercentage,
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [improvedPrompt, setImprovedPrompt] = useState("");

  const getSuccessRateColor = (percentage: number): string => {
    if (percentage >= 90) return "text-green-400";
    if (percentage >= 50) return "text-yellow-400";
    return "text-red-400";
  };

  const handleImprovePrompt = async () => {
    try {
      const response = await fetch(
        `http://localhost:9000/prompts/${promptId}/improve`,
        {
          method: "GET",
        }
      );
      const data = await response.json();
      setImprovedPrompt(data.improved_prompt);
      setIsModalOpen(true);
    } catch (error) {
      console.error("Failed to improve prompt:", error);
    }
  };

  return (
    <header className="bg-gray-800 p-6 text-white">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h1 className="text-3xl font-bold mb-2">{promptName}</h1>
          <p className="text-lg mb-2">Model: {modelName}</p>
          {correctPercentage !== null && (
            <p
              className={`text-lg mb-2 ${getSuccessRateColor(
                correctPercentage
              )}`}
            >
              Success Rate: {correctPercentage}%
            </p>
          )}
        </div>
        <Button
          variant="contained"
          color="primary"
          onClick={handleImprovePrompt}
          className="bg-teal-500 hover:bg-teal-600 text-white"
        >
          Improve Prompt
        </Button>
      </div>
      <div className="w-full bg-gray-700 p-4 rounded-lg">
        <h2 className="text-xl font-semibold mb-2">Prompt Under Test</h2>
        <p className="text-lg text-gray-300">{prompt}</p>
      </div>

      <Modal
        open={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        aria-labelledby="improved-prompt-modal"
      >
        <Box className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-11/12 max-w-2xl max-h-[90vh] bg-gray-900 border-2 border-teal-500 rounded-lg p-6 overflow-hidden flex flex-col">
          <h2
            id="improved-prompt-modal"
            className="text-2xl font-bold mb-4 text-teal-400"
          >
            Improved Prompt
          </h2>
          <div className="flex-grow overflow-auto mb-4">
            <TextareaAutosize
              value={improvedPrompt}
              readOnly
              className="w-full p-3 bg-gray-800 text-white border border-gray-600 rounded"
              style={{ resize: "none" }}
            />
          </div>
          <Button
            variant="contained"
            color="primary"
            onClick={() => setIsModalOpen(false)}
            className="bg-teal-500 hover:bg-teal-600 text-white"
          >
            Close
          </Button>
        </Box>
      </Modal>
    </header>
  );
};

export default Header;
