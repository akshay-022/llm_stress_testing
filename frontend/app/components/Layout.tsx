"use client";
import React, { useState, useEffect } from "react";
import TestCaseTable from "./TestCaseTable";

interface Prompt {
  id: number;
  prompt: string;
  prompt_name: string;
  model_name: string;
  process_id: number;
}

const Layout = ({ children }: { children: React.ReactNode }) => {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [selectedPromptId, setSelectedPromptId] = useState<number | null>(null);

  useEffect(() => {
    const fetchPrompts = async () => {
      try {
        const response = await fetch("http://localhost:9000/prompts");
        if (!response.ok) {
          throw new Error("Failed to fetch prompts");
        }
        const data = await response.json();
        setPrompts(data);
      } catch (error) {
        console.error("Error fetching prompts:", error);
      }
    };

    fetchPrompts();
  }, []);

  const handlePromptClick = (promptId: number) => {
    setSelectedPromptId(promptId);
  };

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 bg-gray-800 text-white p-4 overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">Prompt Names</h2>
        <ul className="space-y-2">
          {prompts.map((prompt) => (
            <li
              key={prompt.id}
              className="hover:bg-gray-700 p-2 rounded cursor-pointer"
              onClick={() => handlePromptClick(prompt.id)}
            >
              {prompt.prompt_name}
            </li>
          ))}
        </ul>
      </aside>
      <div className="flex-1">
        <main className="p-4">
          {selectedPromptId ? (
            <TestCaseTable promptId={selectedPromptId} />
          ) : (
            children
          )}
        </main>
      </div>
    </div>
  );
};

export default Layout;
