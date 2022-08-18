import { useQuery } from 'react-query';
import { formatDate } from './MessageList';

const API_URL = `http://192.168.1.11:3000/api`;

export function Home() {
  const { isLoading, error, data } = useQuery(
    'stats',
    () => fetch(`${API_URL}/stats`).then((res) => res.json()),
    {
      refetchInterval: 1000,
    }
  );

  return (
    <>
      <div class="stats">
        <div className="info-block">
          <span className="value">{data != null && data.messageCount}</span>
          <span className="label">Total Messages</span>
        </div>
        <div className="info-block">
          <span className="value">
            {data != null && formatDate(data.lastMessage.created_at)}
          </span>
          <span className="label">Last Message Recorded</span>
        </div>
        <div className="info-block">
          <span className="value">{data != null && data.totalListens}</span>
          <span className="label">Total Listens</span>
        </div>
      </div>
    </>
  );
}
