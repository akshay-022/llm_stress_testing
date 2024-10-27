"use client";
import React, { useState, useEffect } from "react";
import TestCaseTable from "./TestCaseTable";
import Header from "./Header";
import { motion } from "framer-motion";

interface Prompt {
  id: number;
  prompt: string;
  prompt_name: string;
  model_name: string;
  process_id: number;
}

const Layout = ({ children }: { children: React.ReactNode }) => {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null);

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

  const handlePromptClick = (prompt: Prompt) => {
    setSelectedPrompt(prompt);
  };

  return (
    <div className="flex min-h-screen bg-gray-900">
      <motion.aside
        initial={{ x: -300 }}
        animate={{ x: 0 }}
        transition={{ type: "spring", stiffness: 100 }}
        className="w-64 bg-gray-800 text-gray-300 p-6 overflow-y-auto"
      >
        <h2 className="text-2xl font-bold mb-6 text-teal-400">Prompt Names</h2>
        <ul className="space-y-2">
          {prompts.map((prompt) => (
            <motion.li
              key={prompt.id}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.98 }}
              className="hover:bg-gray-700 p-3 rounded-md cursor-pointer transition-all duration-200"
              onClick={() => handlePromptClick(prompt)}
            >
              {prompt.prompt_name}
            </motion.li>
          ))}
        </ul>
      </motion.aside>
      <div className="flex-1 flex flex-col">
        {selectedPrompt && (
          <Header
            promptName={selectedPrompt.prompt_name}
            prompt={selectedPrompt.prompt}
            modelName={selectedPrompt.model_name}
          />
        )}
        <main className="p-8 flex-1">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {selectedPrompt ? (
              <TestCaseTable promptId={selectedPrompt.id} />
            ) : (
              children
            )}
          </motion.div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
