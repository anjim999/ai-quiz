import React from "react";

export default function HistoryTable({ items, onDetails }) {
  return (
    <div className="card overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="text-left border-b">
            <th className="py-2">ID</th>
            <th className="py-2">Title</th>
            <th className="py-2">URL</th>
            <th className="py-2">Generated</th>
            <th className="py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {items?.length ? items.map(row => (
            <tr key={row.id} className="border-b">
              <td className="py-2 pr-3">{row.id}</td>
              <td className="py-2 pr-3">{row.title}</td>
              <td className="py-2 pr-3 max-w-[380px] truncate">{row.url}</td>
              <td className="py-2 pr-3">{new Date(row.date_generated).toLocaleString()}</td>
              <td className="py-2">
                <button className="btn btn-primary" onClick={() => onDetails(row.id)}>Details</button>
              </td>
            </tr>
          )) : (
            <tr><td colSpan="5" className="py-6 text-center text-gray-500">No history yet</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
