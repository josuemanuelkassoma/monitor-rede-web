// src/components/ChartLine.jsx
import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function ChartLine({ data, xKey, yKey, title }) {
  return (
    <div style={{ width: '100%', height: 300, margin: '1rem 0' }}>
      <h3 style={{ textAlign: 'center' }}>{title}</h3>
      <ResponsiveContainer>
        <LineChart data={data}>
          <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Line type="monotone" dataKey={yKey} stroke="#007bff" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
