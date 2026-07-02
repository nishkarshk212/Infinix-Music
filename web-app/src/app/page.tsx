'use client';

import { useState, useEffect } from 'react';
import {
  Play,
  Pause,
  SkipForward,
  SkipBack,
  Repeat,
  Shuffle,
  Volume2,
  Heart,
  Search,
  Home as HomeIcon,
  Library,
  Settings,
  BarChart3,
  CreditCard,
  Users,
  Bell,
  Zap,
  Music,
  ShieldCheck,
  Globe,
  LogOut,
  Download,
  TrendingUp,
  Star,
  ShoppingCart,
  Wallet,
  MessageSquare,
  HelpCircle,
  User
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  AreaChart,
  Area
} from 'recharts';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: any[]) {
  return twMerge(clsx(inputs));
}

const apiUsageData = [
  { day: 'Mon', requests: 400, quota: 1000 },
  { day: 'Tue', requests: 300, quota: 1000 },
  { day: 'Wed', requests: 500, quota: 1000 },
  { day: 'Thu', requests: 800, quota: 1000 },
  { day: 'Fri', requests: 450, quota: 1000 },
  { day: 'Sat', requests: 1200, quota: 1000 },
  { day: 'Sun', requests: 600, quota: 1000 },
];

const trendingSongs = [
  { id: 1, title: 'Nightcall', artist: 'Kavinsky', cover: 'https://images.unsplash.com/photo-1493225255756-d9584f8606e9?q=80&w=300&auto=format&fit=crop', duration: '4:12' },
  { id: 2, title: 'Instant Crush', artist: 'Daft Punk', cover: 'https://images.unsplash.com/photo-1459749411175-04bf5292ceea?q=80&w=300&auto=format&fit=crop', duration: '5:37' },
  { id: 3, title: 'Digital Love', artist: 'Daft Punk', cover: 'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?q=80&w=300&auto=format&fit=crop', duration: '4:58' },
  { id: 4, title: 'Starboy', artist: 'The Weeknd', cover: 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?q=80&w=300&auto=format&fit=crop', duration: '3:50' },
  { id: 5, title: 'Blinding Lights', artist: 'The Weeknd', cover: 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?q=80&w=300&auto=format&fit=crop', duration: '3:20' },
];

const apiPlans = [
  { name: 'Free Trial', price: '$0', requests: '100/day', features: ['Basic Search', 'Standard Quality', 'Community Support'] },
  { name: 'Starter', price: '$9.99', requests: '1,000/day', features: ['HD Quality', 'Priority Queue', 'Email Support', '1 API Key'] },
  { name: 'Basic', price: '$29.99', requests: '10,000/day', features: ['4K Quality', 'Faster Processing', 'Live Chat', '5 API Keys'] },
  { name: 'Pro', price: '$99.99', requests: '100,000/day', features: ['8K Quality', 'Custom Integrations', '24/7 Support', 'Unlimited Keys'] },
];

const ParticleBackground = () => {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-pink-600/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
    </div>
  );
};

const GlassCard = ({ children, className, delay = 0 }: { children: React.ReactNode; className?: string; delay?: number }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay }}
    className={cn("glass rounded-3xl p-6", className)}
  >
    {children}
  </motion.div>
);

const NeonButton = ({ children, onClick, variant = 'primary', className, icon: Icon }: any) => {
  const variants = {
    primary: 'bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 hover:shadow-lg hover:shadow-purple-500/50',
    secondary: 'bg-white/10 hover:bg-white/20 border border-white/20',
    outline: 'border-2 border-purple-500 text-purple-400 hover:bg-purple-500/10'
  };

  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={cn(
        "px-8 py-3 rounded-full font-semibold flex items-center gap-2 transition-all duration-300",
        variants[variant as keyof typeof variants],
        className
      )}
    >
      {Icon && <Icon size={20} />}
      {children}
    </motion.button>
  );
};

export default function Home() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentSong, setCurrentSong] = useState(trendingSongs[0]);
  const [volume, setVolume] = useState(70);

  const tabs = [
    { id: 'dashboard', label: 'Home', icon: HomeIcon },
    { id: 'marketplace', label: 'Marketplace', icon: ShoppingCart },
    { id: 'library', label: 'Library', icon: Library },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen pb-32">
      <ParticleBackground />

      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
              <Music className="text-white" />
            </div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              Infinix Music
            </h1>
          </div>

          <div className="flex items-center gap-4">
            <button className="p-2 rounded-full hover:bg-white/10 transition-colors">
              <Bell size={20} />
            </button>
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
                <User size={18} />
              </div>
              <span className="hidden md:block font-medium">Alone Coder</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 pt-24">
        <AnimatePresence mode="wait">
          {activeTab === 'dashboard' && (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              {/* Welcome Section */}
              <div className="mb-8">
                <h2 className="text-3xl md:text-4xl font-bold mb-2">Welcome back! 🎵</h2>
                <p className="text-gray-400">What would you like to listen to today?</p>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                {[
                  { label: 'Total Plays', value: '12.5K', icon: Play, color: 'from-purple-500 to-purple-600' },
                  { label: 'Favorites', value: '234', icon: Heart, color: 'from-pink-500 to-pink-600' },
                  { label: 'API Calls', value: '8.2K', icon: Zap, color: 'from-blue-500 to-blue-600' },
                  { label: 'Premium', value: 'Active', icon: Star, color: 'from-yellow-500 to-yellow-600' },
                ].map((stat, i) => (
                  <GlassCard key={i} delay={i * 0.1}>
                    <div className="flex items-center justify-between mb-4">
                      <div className={cn("w-12 h-12 rounded-2xl bg-gradient-to-br", stat.color, "flex items-center justify-center")}>
                        <stat.icon className="text-white" size={24} />
                      </div>
                    </div>
                    <h3 className="text-2xl font-bold mb-1">{stat.value}</h3>
                    <p className="text-gray-400 text-sm">{stat.label}</p>
                  </GlassCard>
                ))}
              </div>

              {/* Trending & Player */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                {/* Trending Songs */}
                <GlassCard className="lg:col-span-2" delay={0.2}>
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-bold flex items-center gap-2">
                      <TrendingUp className="text-pink-500" /> Trending Now
                    </h3>
                    <button className="text-purple-400 hover:text-purple-300 text-sm font-medium">See All</button>
                  </div>

                  <div className="space-y-4">
                    {trendingSongs.map((song, i) => (
                      <motion.div
                        key={song.id}
                        whileHover={{ scale: 1.02, backgroundColor: 'rgba(255,255,255,0.05)' }}
                        className="flex items-center gap-4 p-3 rounded-2xl cursor-pointer transition-all"
                        onClick={() => {
                          setCurrentSong(song);
                          setIsPlaying(true);
                        }}
                      >
                        <span className="text-gray-500 w-6">{i + 1}</span>
                        <img
                          src={song.cover}
                          alt={song.title}
                          className="w-14 h-14 rounded-xl object-cover"
                        />
                        <div className="flex-1">
                          <h4 className="font-semibold">{song.title}</h4>
                          <p className="text-sm text-gray-400">{song.artist}</p>
                        </div>
                        <span className="text-sm text-gray-500">{song.duration}</span>
                        <button className="p-2 rounded-full hover:bg-white/10">
                          <Heart size={18} className="text-gray-400" />
                        </button>
                      </motion.div>
                    ))}
                  </div>
                </GlassCard>

                {/* Quick Actions */}
                <GlassCard delay={0.3}>
                  <h3 className="text-xl font-bold mb-6">Quick Actions</h3>
                  <div className="space-y-4">
                    <NeonButton icon={Search} className="w-full justify-center">Search Music</NeonButton>
                    <NeonButton icon={ShoppingCart} variant="secondary" className="w-full justify-center">API Marketplace</NeonButton>
                    <NeonButton icon={Wallet} variant="outline" className="w-full justify-center">Wallet</NeonButton>
                  </div>
                </GlassCard>
              </div>
            </motion.div>
          )}

          {activeTab === 'marketplace' && (
            <motion.div
              key="marketplace"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="mb-8">
                <h2 className="text-3xl md:text-4xl font-bold mb-2">YouTube API Marketplace</h2>
                <p className="text-gray-400">Choose the perfect plan for your needs</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                {apiPlans.map((plan, i) => (
                  <GlassCard key={i} delay={i * 0.1} className={i === 1 ? "ring-2 ring-purple-500 relative" : ""}>
                    {i === 1 && (
                      <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gradient-to-r from-purple-600 to-pink-600 px-4 py-1 rounded-full text-sm font-semibold">
                        Popular
                      </div>
                    )}
                    <div className="text-center mb-6">
                      <h3 className="text-xl font-bold mb-2">{plan.name}</h3>
                      <div className="text-4xl font-bold mb-2">{plan.price}</div>
                      <p className="text-gray-400">{plan.requests}</p>
                    </div>
                    <ul className="space-y-3 mb-6">
                      {plan.features.map((feature, j) => (
                        <li key={j} className="flex items-center gap-2 text-sm">
                          <div className="w-5 h-5 rounded-full bg-green-500/20 flex items-center justify-center">
                            <ShieldCheck size={12} className="text-green-400" />
                          </div>
                          {feature}
                        </li>
                      ))}
                    </ul>
                    <NeonButton className="w-full justify-center" variant={i === 1 ? "primary" : "secondary"}>
                      Get Started
                    </NeonButton>
                  </GlassCard>
                ))}
              </div>

              {/* Usage Analytics */}
              <GlassCard delay={0.4}>
                <h3 className="text-xl font-bold mb-6">API Usage Analytics</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={apiUsageData}>
                      <defs>
                        <linearGradient id="colorRequests" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#a855f7" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="day" stroke="#9ca3af" />
                      <YAxis stroke="#9ca3af" />
                      <Tooltip
                        contentStyle={{ backgroundColor: 'rgba(0,0,0,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                      />
                      <Area type="monotone" dataKey="requests" stroke="#a855f7" strokeWidth={3} fillOpacity={1} fill="url(#colorRequests)" />
                      <Area type="monotone" dataKey="quota" stroke="#3b82f6" strokeWidth={2} strokeDasharray="5 5" fill="none" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </GlassCard>
            </motion.div>
          )}

          {activeTab === 'library' && (
            <motion.div
              key="library"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="mb-8">
                <h2 className="text-3xl md:text-4xl font-bold mb-2">Your Library</h2>
                <p className="text-gray-400">Your saved music and playlists</p>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                {[1, 2, 3, 4].map((i) => (
                  <GlassCard key={i} delay={i * 0.1} className="text-center cursor-pointer">
                    <div className="w-full aspect-square rounded-2xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 mb-4 flex items-center justify-center">
                      <Music size={48} className="text-purple-400" />
                    </div>
                    <h4 className="font-semibold mb-1">Playlist {i}</h4>
                    <p className="text-sm text-gray-400">24 songs</p>
                  </GlassCard>
                ))}
              </div>
            </motion.div>
          )}

          {activeTab === 'analytics' && (
            <motion.div
              key="analytics"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="mb-8">
                <h2 className="text-3xl md:text-4xl font-bold mb-2">Analytics</h2>
                <p className="text-gray-400">Detailed insights and reports</p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <GlassCard delay={0.1}>
                  <h3 className="text-xl font-bold mb-6">Listening Activity</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={apiUsageData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                        <XAxis dataKey="day" stroke="#9ca3af" />
                        <YAxis stroke="#9ca3af" />
                        <Tooltip
                          contentStyle={{ backgroundColor: 'rgba(0,0,0,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                        />
                        <Bar dataKey="requests" fill="url(#colorBar)" radius={[8, 8, 0, 0]} />
                        <defs>
                          <linearGradient id="colorBar" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#ec4899"/>
                            <stop offset="95%" stopColor="#8b5cf6"/>
                          </linearGradient>
                        </defs>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </GlassCard>

                <GlassCard delay={0.2}>
                  <h3 className="text-xl font-bold mb-6">Top Artists</h3>
                  <div className="space-y-4">
                    {['Daft Punk', 'The Weeknd', 'Kavinsky', 'Tame Impala'].map((artist, i) => (
                      <div key={i} className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center font-bold">
                          {i + 1}
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold">{artist}</h4>
                          <p className="text-sm text-gray-400">{100 - i * 15} plays</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </GlassCard>
              </div>
            </motion.div>
          )}

          {activeTab === 'settings' && (
            <motion.div
              key="settings"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="mb-8">
                <h2 className="text-3xl md:text-4xl font-bold mb-2">Settings</h2>
                <p className="text-gray-400">Customize your experience</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[
                  { icon: User, title: 'Profile', desc: 'Edit your profile information' },
                  { icon: Globe, title: 'Language', desc: 'Choose your preferred language' },
                  { icon: Bell, title: 'Notifications', desc: 'Manage notification preferences' },
                  { icon: ShieldCheck, title: 'Security', desc: '2FA and account security' },
                  { icon: MessageSquare, title: 'Support', desc: 'Contact our support team' },
                  { icon: HelpCircle, title: 'FAQ', desc: 'Frequently asked questions' },
                ].map((item, i) => (
                  <GlassCard key={i} delay={i * 0.1} className="flex items-center gap-4 cursor-pointer hover:bg-white/5 transition-colors">
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center">
                      <item.icon className="text-purple-400" />
                    </div>
                    <div>
                      <h4 className="font-semibold">{item.title}</h4>
                      <p className="text-sm text-gray-400">{item.desc}</p>
                    </div>
                  </GlassCard>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Bottom Navigation (Mobile) & Player */}
      <div className="fixed bottom-0 left-0 right-0 z-50">
        {/* Mini Player */}
        <motion.div
          initial={{ y: 100 }}
          animate={{ y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass border-t border-white/10 px-4 py-4"
        >
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center gap-4">
              <img
                src={currentSong.cover}
                alt={currentSong.title}
                className="w-14 h-14 rounded-xl object-cover"
              />
              <div className="flex-1 min-w-0">
                <h4 className="font-semibold truncate">{currentSong.title}</h4>
                <p className="text-sm text-gray-400 truncate">{currentSong.artist}</p>
              </div>

              <div className="hidden md:flex items-center gap-2">
                <button className="p-2 hover:bg-white/10 rounded-full">
                  <Shuffle size={18} className="text-gray-400" />
                </button>
                <button className="p-2 hover:bg-white/10 rounded-full">
                  <SkipBack size={24} />
                </button>
              </div>

              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => setIsPlaying(!isPlaying)}
                className="w-12 h-12 rounded-full bg-gradient-to-r from-purple-600 to-pink-600 flex items-center justify-center shadow-lg shadow-purple-500/50"
              >
                {isPlaying ? <Pause size={24} fill="white" /> : <Play size={24} fill="white" className="ml-1" />}
              </motion.button>

              <div className="hidden md:flex items-center gap-2">
                <button className="p-2 hover:bg-white/10 rounded-full">
                  <SkipForward size={24} />
                </button>
                <button className="p-2 hover:bg-white/10 rounded-full">
                  <Repeat size={18} className="text-gray-400" />
                </button>
                <div className="flex items-center gap-2 ml-4">
                  <Volume2 size={18} className="text-gray-400" />
                  <div className="w-24 h-1 bg-white/10 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                      style={{ width: `${volume}%` }}
                    />
                  </div>
                </div>
              </div>

              <div className="flex md:hidden items-center gap-2">
                <button className="p-2 hover:bg-white/10 rounded-full">
                  <Heart size={18} className="text-gray-400" />
                </button>
                <button className="p-2 hover:bg-white/10 rounded-full">
                  <SkipForward size={24} />
                </button>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Bottom Nav */}
        <nav className="glass border-t border-white/10 md:hidden">
          <div className="flex items-center justify-around py-3">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    "flex flex-col items-center gap-1 p-2 transition-all",
                    isActive ? "text-purple-400" : "text-gray-400"
                  )}
                >
                  <Icon
                    size={24}
                    className={cn(
                      "transition-transform",
                      isActive && "scale-110"
                    )}
                  />
                  <span className="text-xs font-medium">{tab.label}</span>
                </button>
              );
            })}
          </div>
        </nav>
      </div>

      {/* Desktop Sidebar Nav */}
      <nav className="hidden md:flex fixed left-0 top-24 bottom-0 w-20 flex-col items-center py-8 gap-4 glass border-r border-white/10">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <motion.button
              key={tab.id}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "w-12 h-12 rounded-2xl flex items-center justify-center transition-all",
                isActive
                  ? "bg-gradient-to-r from-purple-600 to-pink-600 shadow-lg shadow-purple-500/30"
                  : "hover:bg-white/10 text-gray-400"
              )}
            >
              <Icon size={24} />
            </motion.button>
          );
        })}
      </nav>
    </div>
  );
}
