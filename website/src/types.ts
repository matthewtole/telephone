export interface Message {
  id: number;
  created_at: string;
  play_count: number;
  last_played_at?: string;
  filename: string;
  duration: number;
}
