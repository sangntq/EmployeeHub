/**
 * 社員詳細 — マネージャーメモタブ
 * LocalStorage を使ってメモを保存する（サーバーサイド永続化は将来対応）
 */
import { useState, useEffect } from 'react'
import { Button, Input, Space, Typography, Empty, Tag, Divider } from 'antd'
import { PlusOutlined, DeleteOutlined, SaveOutlined } from '@ant-design/icons'
import { useTranslation } from 'react-i18next'

const { TextArea } = Input
const { Text } = Typography

interface Note {
  id: string
  content: string
  createdAt: string
  updatedAt: string
}

interface NotesTabProps {
  employeeId: string
  canEdit: boolean
}

const STORAGE_KEY = (id: string) => `employeehub-notes-${id}`

function loadNotes(employeeId: string): Note[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY(employeeId))
    return raw ? (JSON.parse(raw) as Note[]) : []
  } catch {
    return []
  }
}

function saveNotes(employeeId: string, notes: Note[]): void {
  localStorage.setItem(STORAGE_KEY(employeeId), JSON.stringify(notes))
}

export default function NotesTab({ employeeId, canEdit }: NotesTabProps) {
  const { t } = useTranslation()
  const [notes, setNotes] = useState<Note[]>(() => loadNotes(employeeId))
  const [draft, setDraft] = useState('')
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editContent, setEditContent] = useState('')

  // employeeId が変わったらノートを再ロード
  useEffect(() => {
    setNotes(loadNotes(employeeId))
    setDraft('')
    setEditingId(null)
  }, [employeeId])

  const handleAdd = () => {
    if (!draft.trim()) return
    const newNote: Note = {
      id: `note-${Date.now()}`,
      content: draft.trim(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    const updated = [newNote, ...notes]
    setNotes(updated)
    saveNotes(employeeId, updated)
    setDraft('')
  }

  const handleDelete = (id: string) => {
    const updated = notes.filter(n => n.id !== id)
    setNotes(updated)
    saveNotes(employeeId, updated)
  }

  const handleEditStart = (note: Note) => {
    setEditingId(note.id)
    setEditContent(note.content)
  }

  const handleEditSave = (id: string) => {
    if (!editContent.trim()) return
    const updated = notes.map(n =>
      n.id === id ? { ...n, content: editContent.trim(), updatedAt: new Date().toISOString() } : n
    )
    setNotes(updated)
    saveNotes(employeeId, updated)
    setEditingId(null)
    setEditContent('')
  }

  const formatDate = (iso: string) =>
    new Date(iso).toLocaleString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })

  return (
    <div style={{ maxWidth: 720 }}>
      {/* 新規メモ入力エリア */}
      {canEdit && (
        <div style={{ marginBottom: 24 }}>
          <Text strong style={{ display: 'block', marginBottom: 8 }}>
            {t('notes.newNote')}
          </Text>
          <TextArea
            rows={4}
            value={draft}
            onChange={e => setDraft(e.target.value)}
            placeholder={t('notes.placeholder')}
            style={{ marginBottom: 8 }}
          />
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleAdd}
            disabled={!draft.trim()}
          >
            {t('notes.addNote')}
          </Button>
        </div>
      )}

      {/* メモ一覧 */}
      {notes.length === 0 ? (
        <Empty description={t('notes.empty')} image={Empty.PRESENTED_IMAGE_SIMPLE} />
      ) : (
        <Space direction="vertical" style={{ width: '100%' }} size={12}>
          {notes.map(note => (
            <div
              key={note.id}
              style={{
                background: '#FFFBEB',
                border: '1px solid #FDE68A',
                borderRadius: 8,
                padding: '12px 16px',
              }}
            >
              {editingId === note.id ? (
                <Space direction="vertical" style={{ width: '100%' }}>
                  <TextArea
                    rows={3}
                    value={editContent}
                    onChange={e => setEditContent(e.target.value)}
                    autoFocus
                  />
                  <Space>
                    <Button
                      size="small"
                      type="primary"
                      icon={<SaveOutlined />}
                      onClick={() => handleEditSave(note.id)}
                    >
                      {t('action.save')}
                    </Button>
                    <Button size="small" onClick={() => setEditingId(null)}>
                      {t('action.cancel')}
                    </Button>
                  </Space>
                </Space>
              ) : (
                <>
                  <Text style={{ whiteSpace: 'pre-wrap', display: 'block', marginBottom: 8 }}>
                    {note.content}
                  </Text>
                  <Divider style={{ margin: '8px 0' }} />
                  <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                    <Space size={4}>
                      <Tag color="gold" style={{ fontSize: 11 }}>
                        {formatDate(note.createdAt)}
                      </Tag>
                      {note.updatedAt !== note.createdAt && (
                        <Tag color="default" style={{ fontSize: 11 }}>
                          {t('notes.edited')} {formatDate(note.updatedAt)}
                        </Tag>
                      )}
                    </Space>
                    {canEdit && (
                      <Space size={4}>
                        <Button
                          size="small"
                          type="text"
                          onClick={() => handleEditStart(note)}
                        >
                          {t('action.edit')}
                        </Button>
                        <Button
                          size="small"
                          type="text"
                          danger
                          icon={<DeleteOutlined />}
                          onClick={() => handleDelete(note.id)}
                        />
                      </Space>
                    )}
                  </Space>
                </>
              )}
            </div>
          ))}
        </Space>
      )}
    </div>
  )
}
