export function SkeletonRow({ numCells }) {
  return (
    <tr>
      {new Array(numCells).fill(null).map((_, index) => (
        <td key={index}>
          <span className="skeleton">&nbsp;</span>
        </td>
      ))}
    </tr>
  );
}

export function SkeletonTable({ numRows, numColumns }) {
  return new Array(numRows)
    .fill(null)
    .map((_, index) => <SkeletonRow key={index} numCells={numColumns} />);
}
