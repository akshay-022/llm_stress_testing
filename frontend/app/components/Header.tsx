import React from "react";

const Header = ({
  promptName,
  prompt,
  modelName,
}: {
  promptName: string;
  prompt: string;
  modelName: string;
}) => {
  return (
    <header className="bg-gray-800 text-gray-200 p-6 shadow-lg">
      <h1 className="text-3xl font-bold mb-2 text-teal-400">{promptName}</h1>
      <p className="text-sm mb-2 text-gray-400">Model: {modelName}</p>
      <p className="text-gray-300">{prompt}</p>
    </header>
  );
};

export default Header;
