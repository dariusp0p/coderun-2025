import React from "react";

export default function StatusBar({ status, kind = "info" }) {
  if (!status) return null;
  return <div className={`status ${kind}`}>{status}</div>;
}
