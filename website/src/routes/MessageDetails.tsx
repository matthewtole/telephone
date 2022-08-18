import React from 'react';
import { useQuery } from 'react-query';
import { Link, useParams } from 'react-router-dom';
import { API_ROOT, MESSAGES_ROOT } from '../config';
import { formatDate } from './MessageList';
import ReactAudioPlayer from 'react-audio-player';
import { Message } from '../types';
import AudioPlayer from 'react-h5-audio-player';

export function MessageDetails() {
  const { id } = useParams();

  const { data } = useQuery<{
    message: Message;
    previous?: Message;
    next?: Message;
  }>(`messages/${id}`, () =>
    fetch(`${API_ROOT}/message/${id}`).then((res) => res.json())
  );

  if (data == null) {
    return <></>;
  }

  return (
    <>
      <header className="message__header">
        {data.previous == null ? (
          <span></span>
        ) : (
          <Link to={`../${data.previous.id}`}>⟵ Previous</Link>
        )}
        {data.next != null && <Link to={`../${data.next.id}`}>Next ⟶</Link>}
      </header>
      <section style={{ maxWidth: '50em', margin: '0 auto' }}>
        <h2>Recording #{data.message.id}</h2>
        <p>Recorded at {formatDate(data.message.created_at)}</p>
        <p>Played {data.message.play_count} times</p>
        {data.message.play_count > 0 && (
          <p>Last played at {data.message.last_played_at}</p>
        )}
      </section>
      <section style={{ maxWidth: '50em', margin: '0 auto' }}>
        <AudioPlayer
          src={`${MESSAGES_ROOT}/${data.message.filename}`}
          layout="horizontal"
          customAdditionalControls={[]}
          customVolumeControls={[]}
          showJumpControls={false}
          showSkipControls={false}
        />
      </section>
    </>
  );
}
