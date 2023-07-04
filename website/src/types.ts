export interface Message {
  id: number;
  created_at: string;
  play_count: number;
  last_played_at?: string;
  filename: string;
  duration: number;
  process_state: number;
}

export interface Play {
  id: number;
  message_id: number;
  played_at: string;
  duration?: number;
}
