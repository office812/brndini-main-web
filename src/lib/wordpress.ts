const WORDPRESS_URL = process.env.WORDPRESS_URL || 'https://brndini.co.il';
const WORDPRESS_USERNAME = process.env.WORDPRESS_USERNAME || '';
const WORDPRESS_APP_PASSWORD = process.env.WORDPRESS_APP_PASSWORD || '';

function getAuthHeaders(): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (WORDPRESS_USERNAME && WORDPRESS_APP_PASSWORD) {
    const token = Buffer.from(`${WORDPRESS_USERNAME}:${WORDPRESS_APP_PASSWORD}`).toString('base64');
    headers.Authorization = `Basic ${token}`;
  }

  return headers;
}

export interface WPPage {
  id: number;
  slug: string;
  status: string;
  title: { rendered: string };
  content: { rendered: string };
  link: string;
  date: string;
  modified: string;
}

export interface WPPost {
  id: number;
  slug: string;
  status: string;
  title: { rendered: string };
  content: { rendered: string };
  excerpt: { rendered: string };
  link: string;
  date: string;
  modified: string;
  categories: number[];
  tags: number[];
}

export interface WPCategory {
  id: number;
  name: string;
  slug: string;
  count: number;
}

export interface WPMedia {
  id: number;
  title: { rendered: string };
  source_url: string;
  alt_text: string;
  media_type: string;
}

async function wpFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${WORDPRESS_URL}/wp-json/wp/v2/${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...options?.headers,
    },
  });

  if (!res.ok) {
    throw new Error(`WordPress API error: ${res.status} ${res.statusText}`);
  }

  return res.json();
}

// Pages
export async function getPages(params?: Record<string, string>): Promise<WPPage[]> {
  const query = new URLSearchParams({ per_page: '100', ...params }).toString();
  return wpFetch<WPPage[]>(`pages?${query}`);
}

export async function getPage(id: number): Promise<WPPage> {
  return wpFetch<WPPage>(`pages/${id}`);
}

export async function getPageBySlug(slug: string): Promise<WPPage | null> {
  const pages = await wpFetch<WPPage[]>(`pages?slug=${slug}`);
  return pages[0] || null;
}

export async function updatePage(id: number, data: Partial<WPPage>): Promise<WPPage> {
  return wpFetch<WPPage>(`pages/${id}`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// Posts
export async function getPosts(params?: Record<string, string>): Promise<WPPost[]> {
  const query = new URLSearchParams({ per_page: '20', ...params }).toString();
  return wpFetch<WPPost[]>(`posts?${query}`);
}

export async function getPost(id: number): Promise<WPPost> {
  return wpFetch<WPPost>(`posts/${id}`);
}

export async function getPostBySlug(slug: string): Promise<WPPost | null> {
  const posts = await wpFetch<WPPost[]>(`posts?slug=${slug}`);
  return posts[0] || null;
}

export async function updatePost(id: number, data: Partial<WPPost>): Promise<WPPost> {
  return wpFetch<WPPost>(`posts/${id}`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function createPost(data: Partial<WPPost>): Promise<WPPost> {
  return wpFetch<WPPost>('posts', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// Categories
export async function getCategories(): Promise<WPCategory[]> {
  return wpFetch<WPCategory[]>('categories?per_page=100');
}

// Media
export async function getMedia(params?: Record<string, string>): Promise<WPMedia[]> {
  const query = new URLSearchParams({ per_page: '20', ...params }).toString();
  return wpFetch<WPMedia[]>(`media?${query}`);
}

// Site Info
export async function getSiteInfo() {
  const res = await fetch(`${WORDPRESS_URL}/wp-json/`, {
    headers: getAuthHeaders(),
  });
  return res.json();
}
