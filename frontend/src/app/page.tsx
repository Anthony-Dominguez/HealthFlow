'use client'

import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { auth } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    // Check if user is authenticated
    auth.getSession().then(({ data: { session } }) => {
      if (session) {
        router.push('/dashboard')
      }
    })
  }, [router])

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white dark:from-gray-900 dark:to-gray-800">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <nav className="flex justify-between items-center mb-16">
          <h1 className="text-2xl font-bold text-blue-600">HealthFlow+</h1>
          <div className="space-x-4">
            <Link href="/login">
              <Button variant="ghost">Login</Button>
            </Link>
            <Link href="/register">
              <Button>Get Started</Button>
            </Link>
          </div>
        </nav>

        <div className="text-center max-w-4xl mx-auto">
          <h2 className="text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
            Your Health Data, Unified & Intelligent
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
            Transform scattered medical documents into an intelligent, searchable timeline.
            Upload, organize, and chat with your health data using AI.
          </p>
          <div className="flex justify-center gap-4">
            <Link href="/register">
              <Button size="lg" className="text-lg">
                Start Free Trial
              </Button>
            </Link>
            <Link href="/demo">
              <Button size="lg" variant="outline" className="text-lg">
                View Demo
              </Button>
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mt-20">
          <FeatureCard
            icon="📄"
            title="Document Intelligence"
            description="Upload any medical document. Our AI extracts structured data automatically."
          />
          <FeatureCard
            icon="🗓️"
            title="Unified Timeline"
            description="All your health events in one chronological view. Never lose track again."
          />
          <FeatureCard
            icon="💬"
            title="AI Chat Assistant"
            description="Ask questions about your health history in natural language."
          />
          <FeatureCard
            icon="🎤"
            title="Voice Journaling"
            description="Record symptoms and notes with voice. Automatic transcription included."
          />
          <FeatureCard
            icon="🔍"
            title="Semantic Search"
            description="Find information across all documents using AI-powered search."
          />
          <FeatureCard
            icon="🔒"
            title="HIPAA-Ready Security"
            description="Bank-level encryption and row-level security. Your data, your control."
          />
        </div>
      </div>
    </main>
  )
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: string
  title: string
  description: string
}) {
  return (
    <div className="p-6 rounded-lg border bg-card text-card-foreground shadow-sm hover:shadow-md transition-shadow">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-600 dark:text-gray-400">{description}</p>
    </div>
  )
}
