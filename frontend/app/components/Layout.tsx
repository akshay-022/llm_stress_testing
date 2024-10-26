// components/Layout.js
import React from "react";

const Layout = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="flex min-h-screen">
      <aside className="w-64 bg-gray-800 text-white p-4">
        <h2 className="text-xl font-bold">Sidebar</h2>
        {/* Add sidebar content here */}
      </aside>
      <div className="flex-1">
        <header className="bg-gray-900 text-white p-4">
          <h1 className="text-2xl font-bold">Header</h1>
        </header>
        <main className="p-4">{children}</main>
      </div>
    </div>
  );
};

export default Layout;
