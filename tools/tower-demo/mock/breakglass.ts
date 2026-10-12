// The break-glass backend, mocked for the walkthrough: the /breakglass/* routes Tower calls (stateful, so Request,
// Approve, Start, Extend, End and Review move a session the way the real backend does; see tower
// docs/break-glass/admin/internals.md), a fake WebSocket for the attach route that plays a believable shell in the
// hardened debug container, and asciicast v2 recordings hashed with SHA-256 so the player can check them.
//
// Who is signed in is a demo toggle: ?as=sam on the URL, or window.__demo.setUser('sam'), kept in sessionStorage
// along with the sessions so a reload (the walkthrough switches users with one) keeps the story going.
import { sha256HexJs } from '../tower/src/tabs/topology/castPlayback';

type Json = Record<string, any>;
export type DemoUser = 'james' | 'sam' | 'alex';

const USERS: Record<DemoUser, { canBreakGlass: boolean; canReview: boolean; canTerminate: boolean }> = {
  james: { canBreakGlass: false, canReview: true, canTerminate: false }, // owner of the Skyport apps
  sam: { canBreakGlass: false, canReview: true, canTerminate: false }, // another owner
  alex: { canBreakGlass: true, canReview: true, canTerminate: true }, // platform admin
};
const ref = (u: string) => `user:default/${u}`;
const short = (r: string) => r.replace(/^user:[^/]+\//, '');

const KEY = 'demo-breakglass-v1';
const USER_KEY = 'demo-user';
const MIN = 60_000;
const BUCKET = 'tower-breakglass-recordings';

function readUser(): DemoUser {
  try {
    const q = new URLSearchParams(window.location.search).get('as');
    if (q && q in USERS) sessionStorage.setItem(USER_KEY, q);
    const s = sessionStorage.getItem(USER_KEY);
    if (s && s in USERS) return s as DemoUser;
  } catch {
    /* no storage */
  }
  return 'james';
}

export function currentUser(): DemoUser {
  return readUser();
}

interface State {
  sessions: Json[];
  casts: Record<string, string>;
  rekor: number;
}

let state: State | undefined;

function save() {
  try {
    sessionStorage.setItem(KEY, JSON.stringify(state));
  } catch {
    /* fine: in memory only */
  }
}

function load(): State {
  if (state) return state;
  try {
    const raw = sessionStorage.getItem(KEY);
    if (raw) {
      state = JSON.parse(raw);
      return state!;
    }
  } catch {
    /* seed below */
  }
  state = seed();
  save();
  return state;
}

// ---------- the debug container's shell ----------

const NS = 'app-flight-api-prod';
const DB = `flight-db.${NS}.svc.cluster.local`;
const PROMPT = 'debug / $ ';

function answer(cmdline: string, s: Json): string {
  const cmd = cmdline.trim();
  if (!cmd) return '';
  const word = cmd.split(/\s+/)[0];
  const appUser = '1000';
  const ip = s.podIp ?? '10.244.1.20';
  if (cmd === 'id') return 'uid=65532 gid=65532 groups=65532\r\n';
  if (cmd === 'whoami') return 'whoami: unknown uid 65532\r\n';
  if (cmd === 'hostname') return `${s.pod}\r\n`;
  if (word === 'ps') {
    if (s.mode === 'live' && s.processAccess) {
      return [
        'PID   USER     COMMAND',
        `    1 ${appUser}     java -XX:MaxRAMPercentage=75 -jar /app/flight-api.jar`,
        '   87 65532    /bin/sh',
        '   94 65532    ps -o pid,user,args',
      ].join('\r\n') + '\r\n';
    }
    return ['PID   USER     COMMAND', '    1 65532    /bin/sh', '    9 65532    ps -o pid,user,args'].join('\r\n') + '\r\n';
  }
  if (cmd.startsWith('cat /proc/1/environ')) {
    return s.mode === 'live' && s.processAccess ? 'cat: can\'t open \'/proc/1/environ\': Permission denied\r\n' : 'cat: can\'t open \'/proc/1/environ\': No such file or directory\r\n';
  }
  if (word === 'ss') {
    const rows = [
      'State  Recv-Q Send-Q   Local Address:Port    Peer Address:Port Process',
      ...[41822, 41830, 41846, 41858, 41874, 41890, 41902, 41918, 41926, 41940].map(
        p => `ESTAB  0      0         ${ip}:${p}     10.96.84.17:5432`,
      ),
      `ESTAB  0      0          ${ip}:8080      10.244.0.12:52114`,
      `ESTAB  0      0          ${ip}:8080      10.244.2.31:40986`,
    ];
    return rows.join('\r\n') + '\r\n';
  }
  const cache = cmd.includes('fares-cache');
  if (word === 'dig') return cache ? '10.96.91.40\r\n' : '10.96.84.17\r\n';
  if (word === 'nc') {
    const host = cmd.split(/\s+/).find(x => x.includes('.')) ?? DB;
    return cache
      ? `Connection to ${host} (10.96.91.40) 6379 port [tcp/redis] succeeded!\r\n`
      : `Connection to ${host} (10.96.84.17) 5432 port [tcp/postgresql] succeeded!\r\n`;
  }
  if (word === 'curl') return '{"status":"UP","components":{"db":{"status":"UP","details":{"pool":"10/10 active, 14 waiting"}}}}\r\n';
  if (cmd.startsWith('ls /pod-volumes')) {
    return s.volumeAccess
      ? 'config  flight-db-credentials  tmp\r\n'
      : 'ls: /pod-volumes/: No such file or directory\r\n';
  }
  if (word === 'ls') return 'bin    dev    etc    home   lib    media  mnt    opt    proc   root   run    sbin   srv    sys    tmp    usr    var\r\n';
  if (word === 'touch' || word === 'mkdir' || (word === 'echo' && cmd.includes('>'))) {
    const target = cmd.split(/\s+/).pop()?.replace(/^>/, '') ?? '/tmp/x';
    return `${word === 'echo' ? 'sh' : word}: ${target}: Read-only file system\r\n`;
  }
  if (word === 'apk') {
    return 'ERROR: Unable to lock database: Permission denied\r\nERROR: Failed to open apk database: Permission denied\r\n';
  }
  if (word === 'sudo' || word === 'su') return `sh: ${word}: not found\r\n`;
  if (word === 'kubectl') return 'sh: kubectl: not found\r\n';
  if (word === 'exit') return '';
  if (word === 'clear') return '\x1b[H\x1b[2J';
  return `sh: ${word}: not found\r\n`;
}

// asciicast v2 recorder for one session
interface Rec {
  start: number;
  width: number;
  height: number;
  events: Array<[number, string, string]>;
}
const recs = new Map<string, Rec>();
function recOf(id: string): Rec {
  let r = recs.get(id);
  if (!r) {
    r = { start: Date.now(), width: 120, height: 22, events: [] };
    recs.set(id, r);
  }
  return r;
}
function castText(s: Json, r: Rec): string {
  const header = { version: 2, width: r.width, height: r.height, timestamp: Math.floor(r.start / 1000), title: `${s.app} ${s.env} ${s.pod} (${s.id})`, env: { TERM: 'xterm-256color', SHELL: '/bin/sh' } };
  return [JSON.stringify(header), ...r.events.map(e => JSON.stringify([Number(e[0].toFixed(6)), e[1], e[2]]))].join('\n') + '\n';
}

/** A scripted recording for a seeded session: each command typed at a human pace, then its answer. */
function scriptedCast(s: Json, cmds: string[], startMs: number): string {
  const r: Rec = { start: startMs, width: 120, height: 22, events: [] };
  let t = 0.4;
  r.events.push([t, 'o', PROMPT]);
  for (const c of cmds) {
    t += 1.6;
    for (const ch of c) {
      t += 0.07 + ((ch.charCodeAt(0) * 37) % 9) / 100;
      r.events.push([t, 'i', ch]);
      r.events.push([t + 0.004, 'o', ch]);
    }
    t += 0.3;
    r.events.push([t, 'i', '\r']);
    r.events.push([t + 0.004, 'o', '\r\n']);
    t += 0.35;
    r.events.push([t, 'o', answer(c, s) + PROMPT]);
  }
  return castText(s, r);
}

// ---------- seed: the history Tower shows before the walkthrough starts ----------

function id12(seed: string) {
  let h = 2166136261;
  for (const c of seed) h = Math.imul(h ^ c.charCodeAt(0), 16777619) >>> 0;
  let out = '';
  for (let i = 0; i < 12; i++) {
    h = Math.imul(h ^ (h >>> 13), 2246822519) >>> 0;
    out += (h % 36).toString(36);
  }
  return out;
}

export const PROD_PODS = ['flight-api-5c13762f-x7k2p', 'flight-api-5c13762f-q9m4r', 'flight-api-b713762d-h3n8w', 'flight-api-b713762d-d2v6t'];
const POD_IMAGE = 'ghcr.io/skyport/flight-api:1.8.0-4f9c2ab';
const POD_IMAGE_ID = 'ghcr.io/skyport/flight-api@sha256:4f9c2abe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7';

function base(over: Json): Json {
  return {
    app: 'flight-api',
    env: 'prod',
    container: 'flight-api',
    mode: 'copy',
    processAccess: false,
    volumeAccess: false,
    tier: 'flight',
    durationMinutes: 15,
    podImage: POD_IMAGE,
    podImageId: POD_IMAGE_ID,
    ...over,
  };
}

function storeRecording(st: State, s: Json, text: string, endedMs: number) {
  st.casts[s.id] = text;
  const bytes = new TextEncoder().encode(text);
  st.rekor += 3000 + (parseInt(s.id.slice(0, 3), 36) % 900);
  Object.assign(s, {
    recordingKey: `${s.app}/${s.env}/${s.id}.cast`,
    recordingSha256: sha256HexJs(bytes),
    recordingBytes: bytes.length,
    recordingBucket: BUCKET,
    recordingVersion: id12(s.id + 'v').toUpperCase() + 'Qx9',
    recordingRekorIndex: st.rekor,
    recordingRekorUuid: '24296fb24b8ad77a' + sha256HexJs(new TextEncoder().encode(s.id)),
    recordingExpiresAt: new Date(endedMs + 365 * 24 * 60 * MIN).toISOString(),
  });
}

function seed(): State {
  const now = Date.now();
  const st: State = { sessions: [], casts: {}, rekor: 1482090315 };
  const a = base({
    id: id12('seed-sam-copy'),
    pod: PROD_PODS[2],
    mode: 'copy',
    holdApp: true,
    copyPod: `${PROD_PODS[2]}-bg-4k2m`,
    reason: 'Check the copy can reach the new fares cache before the 1.8.0 canary goes past 40%.',
    requester: ref('sam'),
    approver: ref('james'),
    decisionNote: 'Fine, copy with the app held.',
    createdAt: new Date(now - 3 * 1440 * MIN - 95 * MIN).toISOString(),
    approvedAt: new Date(now - 3 * 1440 * MIN - 92 * MIN).toISOString(),
    startedAt: new Date(now - 3 * 1440 * MIN - 90 * MIN).toISOString(),
    expiresAt: new Date(now - 3 * 1440 * MIN - 75 * MIN).toISOString(),
    endedAt: new Date(now - 3 * 1440 * MIN - 81 * MIN).toISOString(),
    endReason: 'ended by user',
    endedBy: ref('sam'),
    state: 'ended',
  });
  storeRecording(st, a, scriptedCast(a, ['id', 'dig +short fares-cache.app-flight-api-prod.svc.cluster.local', 'nc -zv fares-cache.app-flight-api-prod.svc.cluster.local 6379'].map(c => c), Date.parse(a.startedAt)), Date.parse(a.endedAt));
  const b = base({
    id: id12('seed-james-expired'),
    pod: 'flight-api-b713762d-z5c1b',
    reason: 'Boarding sync job retries forever on one flight; want to see what the copy gets back from flight-db.',
    requester: ref('james'),
    createdAt: new Date(now - 11 * 1440 * MIN - 300 * MIN).toISOString(),
    expiresAt: new Date(now - 11 * 1440 * MIN - 270 * MIN).toISOString(),
    endedAt: new Date(now - 11 * 1440 * MIN - 270 * MIN).toISOString(),
    endReason: 'request expired before anyone approved it',
    state: 'ended',
    holdApp: true,
  });
  st.sessions.push(a, b);
  return st;
}

// ---------- routes ----------

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
const err = (status: number, error: string) => json({ error }, status);
const sleep = (ms: number) => new Promise(r => setTimeout(r, ms));

function info() {
  const u = currentUser();
  return { user: ref(u), recordingsConfigured: true, recordingRetentionDays: 365, ...USERS[u] };
}

/** Requests and approvals past their deadline end, as the backend's sweep would. */
function sweep(st: State) {
  const now = Date.now();
  for (const s of st.sessions) {
    if (s.state === 'requested' && Date.parse(s.expiresAt) < now) Object.assign(s, { state: 'ended', endedAt: s.expiresAt, endReason: 'request expired before anyone approved it' });
    if (s.state === 'approved' && Date.parse(s.expiresAt) < now) Object.assign(s, { state: 'ended', endedAt: s.expiresAt, endReason: 'approved but not started within 10 minutes' });
  }
}

const newest = (a: Json, b: Json) => Date.parse(b.createdAt) - Date.parse(a.createdAt);

function queueRow(s: Json) {
  return {
    id: s.id,
    app: s.app,
    env: s.env,
    entityRef: `component:default/${s.app}`,
    pod: s.pod,
    mode: s.mode,
    processAccess: !!s.processAccess,
    volumeAccess: !!s.volumeAccess,
    glassBroken: !!s.glassBroken,
    requester: s.requester,
    approver: s.approver,
    reason: s.reason,
    createdAt: s.createdAt,
    expiresAt: s.expiresAt,
    endedAt: s.endedAt,
    overdue: false,
  };
}

function activate(s: Json) {
  const now = Date.now();
  s.state = 'active';
  s.startedAt = new Date(now).toISOString();
  s.expiresAt = new Date(now + (s.durationMinutes ?? 15) * MIN).toISOString();
  s.attached = false;
  if (s.mode === 'copy') s.copyPod = `${s.pod}-bg-${s.id.slice(0, 4)}`;
  recs.set(s.id, { start: now, width: 120, height: 22, events: [] });
}

export async function breakglassRoute(path: string, q: URLSearchParams, method: string, body: Json | undefined): Promise<Response> {
  const st = load();
  sweep(st);
  const me = ref(currentUser());
  const caps = USERS[currentUser()];

  if (path === '/queue' && method === 'GET') {
    return json({
      toApprove: st.sessions.filter(s => s.state === 'requested' && s.requester !== me).sort(newest).map(queueRow),
      toStart: st.sessions.filter(s => s.state === 'approved' && s.requester === me).sort(newest).map(queueRow),
      toReview: st.sessions.filter(s => s.state === 'ended' && s.glassBroken && s.reviewState === 'due' && s.requester !== me && caps.canReview).sort(newest).map(queueRow),
    });
  }

  if (path === '/sessions' && method === 'GET') {
    const rows = st.sessions.filter(s => s.app === q.get('app') && s.env === q.get('env')).sort(newest).slice(0, 50);
    return json({ sessions: rows, ...info() });
  }

  if (path === '/sessions' && method === 'POST') {
    const b = body ?? {};
    if (!String(b.reason ?? '').trim()) return err(400, 'a reason is required');
    if (st.sessions.some(s => s.state !== 'ended' && s.requester === me)) return err(409, 'you already have a break-glass session or request open; one at a time');
    const flight = b.env === 'prod';
    if (b.glassBroken && !caps.canBreakGlass) return err(403, 'only admins may break the glass');
    await sleep(flight && !b.glassBroken ? 700 : 1800);
    const now = Date.now();
    const s: Json = base({
      id: id12(`${me}-${now}`),
      app: b.appName,
      env: b.env,
      pod: b.podName,
      container: b.container,
      mode: b.mode,
      processAccess: !!b.processAccess,
      volumeAccess: !!b.volumeAccess,
      volumes: b.volumeAccess ? [{ volume: 'config', kind: 'ConfigMap', path: '/pod-volumes/config', appPaths: ['/app/config'] }] : undefined,
      holdApp: b.mode === 'copy' ? !!b.holdApp : undefined,
      sensitive: !!b.volumeAccess || (b.mode === 'live' && !!b.processAccess),
      durationMinutes: b.durationMinutes ?? 15,
      reason: b.reason,
      ticketUrl: b.ticketUrl,
      requester: me,
      createdAt: new Date(now).toISOString(),
      tier: flight ? 'flight' : 'ground',
      podIp: `10.244.${PROD_PODS.indexOf(b.podName) + 1 || 1}.${20 + Math.max(0, PROD_PODS.indexOf(b.podName)) * 3}`,
    });
    if (flight && !b.glassBroken) {
      s.state = 'requested';
      s.expiresAt = new Date(now + 30 * MIN).toISOString();
    } else {
      if (b.glassBroken) {
        s.glassBroken = true;
        s.reviewState = 'due';
      }
      activate(s);
    }
    st.sessions.push(s);
    save();
    return json({ session: s });
  }

  const m = path.match(/^\/sessions\/([a-z0-9]{12})(?:\/([a-z]+))?$/);
  if (!m) return err(404, 'not in demo data');
  const s = st.sessions.find(x => x.id === m[1]);
  if (!s) return err(404, 'no such session');
  const action = m[2];

  if (!action && method === 'GET') return json({ session: s, ...info() });

  if (action === 'recording') {
    const text = st.casts[s.id];
    if (!text) return err(404, 'this session has no recording');
    return new Response(text, { status: 200, headers: { 'Content-Type': 'application/x-asciicast' } });
  }

  if (action === 'approve' || action === 'deny') {
    if (s.requester === me) return err(403, 'you cannot decide your own request');
    if (s.state !== 'requested') return err(409, 'this request is no longer waiting');
    await sleep(500);
    const now = Date.now();
    if (action === 'approve') {
      Object.assign(s, { state: 'approved', approver: me, approvedAt: new Date(now).toISOString(), expiresAt: new Date(now + 10 * MIN).toISOString() });
      if (body?.note) s.decisionNote = body.note;
      if (body?.keepPod) s.recycleWaivedReason = body.keepPodReason;
    } else {
      Object.assign(s, { state: 'ended', approver: me, endedAt: new Date(now).toISOString(), endReason: `denied by ${short(me)}${body?.note ? `: ${body.note}` : ''}` });
    }
    save();
    return json({ session: s });
  }

  if (action === 'start') {
    if (s.requester !== me) return err(403, 'only the requester can start it');
    if (s.state !== 'approved') return err(409, 'this session is not approved');
    await sleep(2200);
    activate(s);
    save();
    return json({ session: s });
  }

  if (action === 'extend') {
    if (s.state !== 'active' || s.extendedAt) return err(409, 'the one extension is used');
    s.extendedAt = new Date().toISOString();
    s.expiresAt = new Date(Date.parse(s.expiresAt) + 15 * MIN).toISOString();
    runtime.get(s.id)?.control({ type: 'extended', expiresAt: s.expiresAt });
    save();
    return json({ session: s });
  }

  if (action === 'end') {
    const now = Date.now();
    if (s.state === 'requested' || s.state === 'approved') {
      Object.assign(s, { state: 'ended', endedAt: new Date(now).toISOString(), endedBy: me, endReason: s.requester === me ? 'withdrawn by the requester' : `cancelled by ${short(me)}` });
      save();
      return json({ session: s });
    }
    if (s.state !== 'active') return err(409, 'already ended');
    await sleep(2600);
    const reason = s.requester === me ? 'ended by user' : `terminated by ${short(me)}`;
    runtime.get(s.id)?.control({ type: 'ended', reason });
    const r = recOf(s.id);
    const end = Date.now();
    Object.assign(s, { state: 'ended', endedAt: new Date(end).toISOString(), endedBy: me, endReason: reason, attached: false });
    if (s.mode === 'live') s.recycled = true;
    storeRecording(st, s, castText(s, r), end);
    save();
    return json({ session: s });
  }

  if (action === 'review') {
    if (!s.glassBroken || s.reviewState !== 'due' || s.state !== 'ended') return err(409, 'nothing to review');
    if (s.requester === me) return err(403, 'someone other than the requester reviews it');
    if (!String(body?.note ?? '').trim()) return err(400, 'a review note is required');
    await sleep(400);
    Object.assign(s, { reviewState: 'done', reviewedBy: me, reviewedAt: new Date().toISOString(), reviewNote: body!.note });
    save();
    return json({ session: s });
  }

  return err(404, 'not in demo data');
}

// ---------- the attach WebSocket ----------

interface Runtime {
  control: (msg: Json) => void;
}
const runtime = new Map<string, Runtime>();
const enc = new TextEncoder();

class FakeBreakglassSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;
  readonly url: string;
  readonly protocol: string;
  readyState = 0;
  binaryType = 'blob';
  onopen: ((ev: any) => void) | null = null;
  onmessage: ((ev: any) => void) | null = null;
  onclose: ((ev: any) => void) | null = null;
  onerror: ((ev: any) => void) | null = null;
  private line = '';
  private session: Json | undefined;
  private rec: Rec | undefined;
  private busy = Promise.resolve();

  constructor(url: string, protocols?: string | string[]) {
    this.url = url;
    this.protocol = Array.isArray(protocols) ? protocols[0] ?? '' : protocols ?? '';
    const id = url.match(/sessions\/([a-z0-9]{12})\/attach/)?.[1];
    setTimeout(() => {
      const st = load();
      this.session = st.sessions.find(s => s.id === id);
      if (!this.session || this.session.state !== 'active') {
        this.readyState = 3;
        this.onclose?.({ code: 4410, reason: 'session is not active' });
        return;
      }
      this.rec = recOf(this.session.id);
      runtime.set(this.session.id, { control: msg => this.text(msg) });
      this.session.attached = true;
      save();
      this.readyState = 1;
      this.onopen?.({});
      this.text({ type: 'attached' });
      setTimeout(() => this.out(PROMPT), 350);
    }, 250);
  }

  addEventListener() {}
  removeEventListener() {}

  private t() {
    return (Date.now() - (this.rec?.start ?? Date.now())) / 1000;
  }

  private text(msg: Json) {
    if (this.readyState !== 1) return;
    this.onmessage?.({ data: JSON.stringify(msg) });
  }

  private out(s: string) {
    if (this.readyState !== 1 || !s) return;
    this.rec?.events.push([this.t(), 'o', s]);
    const bytes = enc.encode(s);
    this.onmessage?.({ data: bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) });
  }

  send(raw: string) {
    let msg: Json;
    try {
      msg = JSON.parse(raw);
    } catch {
      return;
    }
    if (msg.type === 'resize' && this.rec) {
      const first = this.rec.events.length === 0;
      this.rec.width = msg.cols;
      this.rec.height = msg.rows;
      if (!first) this.rec.events.push([this.t(), 'r', `${msg.cols}x${msg.rows}`]);
      return;
    }
    if (msg.type !== 'input' || typeof msg.data !== 'string') return;
    this.rec?.events.push([this.t(), 'i', msg.data]);
    for (const ch of msg.data) this.key(ch);
  }

  private key(ch: string) {
    if (ch === '\r' || ch === '\n') {
      const cmd = this.line;
      this.line = '';
      this.out('\r\n');
      // answers arrive after a short, varied pause, in order
      this.busy = this.busy.then(async () => {
        const ans = answer(cmd, this.session!);
        if (ans) {
          await sleep(cmd.startsWith('dig') || cmd.startsWith('nc') ? 520 : cmd.startsWith('apk') ? 700 : 180);
          this.out(ans);
        }
        this.out(PROMPT);
      });
      return;
    }
    if (ch === '\x7f' || ch === '\b') {
      if (this.line) {
        this.line = this.line.slice(0, -1);
        this.out('\b \b');
      }
      return;
    }
    if (ch === '\x03') {
      this.line = '';
      this.out('^C\r\n' + PROMPT);
      return;
    }
    if (ch >= ' ') {
      this.line += ch;
      this.out(ch);
    }
  }

  close() {
    if (this.readyState === 3) return;
    this.readyState = 3;
    if (this.session) {
      runtime.delete(this.session.id);
      const st = load();
      const s = st.sessions.find(x => x.id === this.session!.id);
      if (s && s.state === 'active') {
        s.attached = false;
        save();
      }
    }
    setTimeout(() => this.onclose?.({ code: 1000, reason: '' }), 0);
  }
}

/** Routes WebSockets for the break-glass attach URL to the fake; everything else (Vite's HMR) stays real. */
export function installFakeWebSocket() {
  const Real = window.WebSocket;
  function Routed(this: any, url: string | URL, protocols?: string | string[]) {
    const u = String(url);
    if (u.includes('/breakglass/')) return new FakeBreakglassSocket(u, protocols);
    return new Real(u, protocols);
  }
  Object.assign(Routed, { CONNECTING: 0, OPEN: 1, CLOSING: 2, CLOSED: 3 });
  Routed.prototype = Real.prototype;
  (window as any).WebSocket = Routed;
}

/** Demo controls for the recording script and for poking at it by hand. */
export function installDemoControls() {
  (window as any).__demo = {
    setUser(u: DemoUser) {
      sessionStorage.setItem(USER_KEY, u);
    },
    user: currentUser,
    reset() {
      sessionStorage.removeItem(KEY);
      state = undefined;
    },
    state: () => load(),
  };
}
