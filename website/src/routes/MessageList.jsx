import { useQuery } from 'react-query';
import { DateTime } from 'luxon';
import { API_ROOT } from '../config';
import { SkeletonTable } from '../components/SkeletonTable';
import { Link } from 'react-router-dom';

export function formatDate(date) {
  return DateTime.fromSQL(date).toFormat('M/dd t');
}

export function formatDuration(duration) {
  const minutes = Math.floor(duration / 60);
  const seconds = duration % 60;
  return [
    minutes.toString().padStart(2, '0'),
    seconds.toString().padStart(2, '0'),
  ].join(':');
}

export function MeessageList() {
  const { isLoading, error, data } = useQuery('messages', () =>
    fetch(`${API_ROOT}/messages`).then((res) => res.json())
  );
  return (
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Created</th>
          <th>Length</th>
          <th># Plays</th>
          <th>Last Play</th>
        </tr>
      </thead>
      <tbody>
        {isLoading && <SkeletonTable numRows={3} numColumns={5} />}
        {data != null &&
          data.map((message) => (
            <tr key={message.id}>
              <td>
                <Link to={`${message.id}`} className="block-link">
                  {message.id}
                </Link>
              </td>
              <td>{formatDate(message.created_at)}</td>
              <td>{formatDuration(message.duration)}</td>
              <td style={{ textAlign: 'right' }}>{message.play_count}</td>
              <td>
                {message.last_played_at != null &&
                  formatDate(message.last_played_at)}
              </td>
            </tr>
          ))}
      </tbody>
    </table>
  );
}
