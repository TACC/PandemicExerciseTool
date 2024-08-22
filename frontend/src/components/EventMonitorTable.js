import React from 'react';
import './EventMonitorTable.css'; // Ensure the CSS file has correct rules

const EventMonitorTable = ({ outputFiles, currentIndex, highlightedIndex }) => {
  return (
    <div className="event-monitor-table">
      <table>
        <thead>
          <tr>
            <th>Day</th>
            <th>Deceased</th>
          </tr>
        </thead>
        <tbody>
          {outputFiles.map((output, index) => {
            // Determine if this row should be highlighted
            const isHighlighted = index === highlightedIndex;
            return (
              <tr
                key={index}
                className={isHighlighted ? 'highlighted' : ''}
              >
                <td>{index}</td>
                <td>
                  {output.data.reduce((acc, county) => {
                    const { D } = county.compartments;
                    const totalDeceased = [
                      ...D.U.L,
                      ...D.U.H,
                      ...D.V.L,
                      ...D.V.H,
                    ].reduce((sum, value) => sum + value, 0);
                    return acc + totalDeceased;
                  }, 0).toFixed(0)} {/* Ensure rounding to whole numbers */}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default EventMonitorTable;
