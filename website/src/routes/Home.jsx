import { useQuery } from 'react-query';
import { API_ROOT } from '../config';
import { formatDate } from './MessageList';

export function Home() {
  const { isLoading, error, data } = useQuery(
    'stats',
    () => fetch(`${API_ROOT}/stats`).then((res) => res.json()),
    {
      refetchInterval: 1000,
    }
  );

  return data != null ? (
    <>
      <div className="stats">
        <a className="info-block" href="/messages">
          <span className="value">{data.messageCount}</span>
          <span className="label">Total Messages</span>
        </a>
        <a className="info-block" href={`/message/${data.lastMessage.id}`}>
          <span className="value">
            {formatDate(data.lastMessage.created_at)}
          </span>
          <span className="label">Last Message Recorded</span>
        </a>
        <div className="info-block">
          <span className="value">{data.totalListens}</span>
          <span className="label">Total Listens</span>
        </div>
      </div>
    </>
  ) : (
    <></>
  );
}
