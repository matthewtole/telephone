import React from 'react';

export const SkeletonRow: React.FC<{ numCells: number }> = ({ numCells }) => {
  return (
    <tr>
      {new Array(numCells).fill(null).map((_, index) => (
        <td key={index}>
          <span className="skeleton">&nbsp;</span>
        </td>
      ))}
    </tr>
  );
};

export const SkeletonTable: React.FC<{
  numRows: number;
  numColumns: number;
}> = ({ numRows, numColumns }) => {
  return (
    <>
      {new Array(numRows).fill(null).map((_, index) => (
        <SkeletonRow key={index} numCells={numColumns} />
      ))}
    </>
  );
};
