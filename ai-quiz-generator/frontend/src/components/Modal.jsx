import React from "react";

export default function Modal({ open, onClose, children, title }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="card max-h-[90vh] w-full max-w-3xl overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">{title}</h3>
          <button className="btn btn-ghost border" onClick={onClose}>Close</button>
        </div>
        {children}
      </div>
    </div>
  );
}
