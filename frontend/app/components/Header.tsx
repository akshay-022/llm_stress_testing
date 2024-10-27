import React from "react";

interface HeaderProps {
  promptName: string;
  prompt: string;
  modelName: string;
  correctPercentage: number | null;
}

const Header: React.FC<HeaderProps> = ({
  promptName,
  prompt,
  modelName,
  correctPercentage,
}) => {
  const getSuccessRateColor = (percentage: number): string => {
    if (percentage >= 90) return "text-green-400";
    if (percentage >= 50) return "text-yellow-400";
    return "text-red-400";
  };

  return (
    <header className="bg-gray-800 p-6 text-white flex justify-between items-start">
      <div>
        <h1 className="text-3xl font-bold mb-2">{promptName}</h1>
        <p className="text-lg mb-2">Model: {modelName}</p>
        {correctPercentage !== null && (
          <p
            className={`text-lg mb-2 ${getSuccessRateColor(correctPercentage)}`}
          >
            Success Rate: {correctPercentage}%
          </p>
        )}
      </div>
      <div className="w-1/2 bg-gray-700 p-4 rounded-lg">
        <h2 className="text-xl font-semibold mb-2">Prompt Under Test</h2>
        <p className="text-lg text-gray-300">{prompt}</p>
      </div>
    </header>
  );
};

export default Header;
