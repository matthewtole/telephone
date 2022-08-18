import { useQuery } from 'react-query';
import { Link, useParams } from 'react-router-dom';
import { API_ROOT, MESSAGES_ROOT } from '../config';
import { formatDate } from './MessageList';
import ReactAudioPlayer from 'react-audio-player';

export function MessageDetails() {
  const { id } = useParams();

  const { data } = useQuery(`messages/${id}`, () =>
    fetch(`${API_ROOT}/message/${id}`).then((res) => res.json())
  );

  if (data == null) {
    return <></>;
  }

  return (
    <>
      <header>
        {data.previous != null && <Link to={`../${data.previous.id}`}>⟵</Link>}
        {data.next != null && <Link to={`../${data.next.id}`}>⟶</Link>}
      </header>
      <section>
        <h2>Recording #{data.message.id}</h2>
        <p>Recorded at {formatDate(data.message.created_at)}</p>
        <p>Played {data.message.play_count} times</p>
        {data.message.play_count > 0 && (
          <p>Last played at {data.message.last_played_at}</p>
        )}
      </section>
      <section>
        <ReactAudioPlayer
          src={`${MESSAGES_ROOT}/${data.message.filename}`}
          controls
        />
      </section>
    </>
  );
}
