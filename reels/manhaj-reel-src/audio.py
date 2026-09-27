import numpy as np, wave
SR=44100; D=23.2; N=int(SR*D); t=np.arange(N)/SR
L=np.zeros(N); R=np.zeros(N)
rng=np.random.default_rng(7)
def add(sig,at,gain=1.0,pan=0.0):
    i=int(at*SR); n=min(len(sig),N-i)
    if n<=0: return
    L[i:i+n]+=sig[:n]*gain*(1-max(0,pan)); R[i:i+n]+=sig[:n]*gain*(1+min(0,pan))
def env(n,a=.005,d=.2):
    x=np.arange(n)/SR; return np.minimum(1,x/a)*np.exp(-x/d)
def lp(x,k):  # one-pole lowpass
    y=np.zeros_like(x); acc=0
    for i in range(len(x)): acc+=k*(x[i]-acc); y[i]=acc
    return y
def kick():
    n=int(.45*SR); x=np.arange(n)/SR; f=45+110*np.exp(-x*28)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,.002,.16)
def hat():
    n=int(.08*SR); s=rng.standard_normal(n); s=s-lp(s,.35); return s*env(n,.001,.018)
def click():
    n=int(.03*SR); s=rng.standard_normal(n); s=s-lp(s,.2); return s*env(n,.0005,.004)
def tick():
    n=int(.05*SR); x=np.arange(n)/SR; return (np.sin(2*np.pi*3200*x)+.5*rng.standard_normal(n))*env(n,.0005,.006)
def whoosh(dur=.55):
    n=int(dur*SR); s=rng.standard_normal(n); k=np.linspace(.02,.35,n)
    y=np.zeros(n); acc=0
    for i in range(n): acc+=k[i]*(s[i]-acc); y[i]=acc
    e=np.sin(np.pi*np.linspace(0,1,n))**2; return y*e*1.6
def boom():
    n=int(1.6*SR); x=np.arange(n)/SR; f=38+60*np.exp(-x*6)
    return (np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,.003,.55)+ .3*lp(rng.standard_normal(n),.05)*env(n,.002,.3))
def pop():
    n=int(.12*SR); x=np.arange(n)/SR; f=900*np.exp(-x*30)+200
    return np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,.001,.03)
# music: 120bpm, chords Am F C G, 2 beats... each chord 2s
bpm=120; beat=60/bpm
chords=[[220,261.6,329.6],[174.6,220,261.6],[261.6/2*2,329.6,392],[196,246.9,293.7]]
bassn=[110,87.3,130.8,98]
pad=np.zeros(N); bass=np.zeros(N)
for ci in range(int(D/2)+1):
    c=chords[ci%4]; a=int(ci*2*SR); b=min(N,a+int(2*SR))
    if a>=N: break
    x=t[a:b]-ci*2; e=np.minimum(1,x/.15)*np.minimum(1,(2-x)/.15)
    for f in c:
        for dt in (-.6,.6): pad[a:b]+=np.sin(2*np.pi*(f*(1+dt/1200*10))*x+dt)*e*.05
    # pluck arp on 8ths
    for k in range(8):
        f=c[k%3]*(2 if k%4==3 else 1); s0=a+int(k*beat/2*SR); n=int(.35*SR)
        if s0+n<N:
            xx=np.arange(n)/SR; add(np.sin(2*np.pi*f*2*xx)*env(n,.002,.09)*.08,s0/SR,1,.3 if k%2 else -.3)
    for k in range(4):
        s0=a+int(k*beat*SR); n=int(beat*SR*.9)
        if s0+n<N:
            xx=np.arange(n)/SR; bass[s0:s0+n]+=np.tanh(2*np.sin(2*np.pi*bassn[ci%4]*xx))*env(n,.01,.25)*.22
mute=np.ones(N)
for a,b in [(4.95,5.55),(16.35,16.9)]:
    mute[int(a*SR):int(b*SR)]=0.15
mute=lp(mute,.0015)
L+=(pad+bass)*mute; R+=(pad+bass)*mute
bt=0.0
while bt<D-.8:
    if not any(a<=bt<b for a,b in [(4.95,5.5),(16.35,16.9)]):
        add(kick(),bt,.75)
        add(hat(),bt+beat/2,.18,.4)
    bt+=beat
for s in [2.4,5.0,6.8,8.8,11.6,14.4,16.4,20.6]: add(whoosh(),s-.35,.35,-.2)
for s in [5.0,16.4,20.6]: add(boom(),s,.8)
for s in [0.35,8.8+.45,8.8+1.2,8.8+1.95,20.6+1.75]: add(click(),s,.6)
for s in [3.0,7.3,12.1,13.4]: add(pop(),s,.35)
for k in range(int(4.2/0.5)): add(tick(),16.4+k*.5,.25,.5 if k%2 else -.5)
# master
fade=np.ones(N); fn=int(1.2*SR); fade[-fn:]=np.linspace(1,0,fn)
fi=int(.05*SR); fade[:fi]=np.linspace(0,1,fi)
st=np.stack([L,R],1)*fade[:,None]
st=np.tanh(st*1.2); st/=np.abs(st).max()/0.89
with wave.open('music.wav','wb') as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((st*32767).astype('<i2').tobytes())
print('ok')
