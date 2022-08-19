import React from 'react';
import { useQuery } from 'react-query';
import { DateTime } from 'luxon';
import { API_ROOT } from '../config';
import { SkeletonTable } from '../components/SkeletonTable';
import { Link, useSearchParams } from 'react-router-dom';
import { Message } from '../types';

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

export function MessageList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const sort = searchParams.get('sort') ?? 'created_at';
  const direction = searchParams.get('direction') ?? 'desc';

  const { isLoading, error, data } = useQuery<Array<Message>>(
    ['messages', sort, direction],
    () =>
      fetch(`${API_ROOT}/messages?sort=${sort}&direction=${direction}`).then(
        (res) => res.json()
      )
  );

  return (
    <main>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>
              <Link to="?sort=created_at">Created</Link>
            </th>
            <th>
              <Link to="?sort=duration">Length</Link>
            </th>
            <th>
              <Link to="?sort=play_count"># Plays</Link>
            </th>
            <th>
              <Link to="?sort=last_played_at">Last Play</Link>
            </th>
          </tr>
        </thead>
        <tbody>
          {isLoading && <SkeletonTable numRows={3} numColumns={5} />}
          {data != null &&
            data.map((message) => (
              <tr key={message.id}>
                <td style={{ fontVariantNumeric: 'tabular-nums' }}>
                  <Link to={`${message.id}`} className="block-link">
                    {message.id.toString().padStart(4, '0')}
                  </Link>
                </td>
                <td>{formatDate(message.created_at)}</td>
                <td style={{ fontVariantNumeric: 'tabular-nums' }}>
                  {formatDuration(message.duration)}
                </td>
                <td
                  style={{
                    fontVariantNumeric: 'tabular-nums',
                    textAlign: 'right',
                  }}
                >
                  {message.play_count}
                </td>
                <td>
                  {message.last_played_at != null &&
                    formatDate(message.last_played_at)}
                </td>
              </tr>
            ))}
        </tbody>
      </table>
    </main>
  );
}
