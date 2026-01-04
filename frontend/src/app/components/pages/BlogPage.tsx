import React, { useEffect, useState } from 'react';
import { BlogService } from '../../../service/blog.service';

export default function BlogPage() {
  const [feed, setFeed] = useState<any[]>([]);

  useEffect(() => {
    const fetchFeed = async () => {
      const res = await BlogService.getFeed({ limit: 10 });
      setFeed(res.items || []); // Khớp với FeedResponse schema
    };
    fetchFeed();
  }, []);

  return (
    <div className="max-w-xl mx-auto py-8">
      <h1 className="text-2xl font-bold mb-6">Tervie blog</h1>
      <div className="space-y-6">
        {feed.map((post) => (
          <div key={post.id} className="bg-white p-4 rounded-lg shadow">
            <div className="flex items-center mb-3">
               <span className="font-semibold">{post.author.username}</span>
            </div>
            <p className="text-gray-800 mb-2">{post.content}</p>
            <div className="flex gap-4 text-sm text-gray-500">
              <span>❤️ {post.likes_count}</span>
              <span>💬 {post.comments_count || 0}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}