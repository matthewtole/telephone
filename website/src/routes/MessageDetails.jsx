import { useQuery } from 'react-query';
import { useParams } from 'react-router-dom';
import { API_ROOT, MESSAGES_ROOT } from '../config';
import { formatDate } from './MessageList';
import ReactAudioPlayer from 'react-audio-player';

export function MessageDetails() {
  const { id } = useParams();
  const { isLoading, error, data } = useQuery('messages-details', () =>
    fetch(`${API_ROOT}/message/${id}`).then((res) => res.json())
  );
  return data == null ? (
    <></>
  ) : (
    <>
      <section>
        <h2>Recording #{data.id}</h2>
        <p>Recorded at {formatDate(data.created_at)}</p>
        <p>Played {data.play_count} times</p>
        {data.play_count > 0 && <p>Last played at {data.last_played_at}</p>}
      </section>
      <section>
        <ReactAudioPlayer src={`${MESSAGES_ROOT}/${data.filename}`} controls />
      </section>
    </>
  );
}
