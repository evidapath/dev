// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.source_record) by
// 05-sanity/generation/gen_schema_files.py. Regenerate rather than
// hand-editing if the JSON Schema changes -- keeps the two in lockstep.
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'sourceRecord',
  title: 'Source Record',
  type: 'document',
  fields: [
    defineField({
      name: 'id',
      title: 'Id',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'url',
      title: 'Url',
      type: 'url',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'source_organization',
      title: 'Source Organization',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'source_type',
      title: 'Source Type',
      type: 'string',
      options: { list: ["official_university", "official_government", "scholarship_provider", "recognized_authority", "secondary"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'title',
      title: 'Title',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'retrieved_at',
      title: 'Retrieved At',
      type: 'string', // unresolved $ref: iso_datetime
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'fields_supported',
      title: 'Fields Supported',
      type: 'array',
      of: [{ type: 'string' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'excerpt',
      title: 'Excerpt',
      type: 'text',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'retrieval_method',
      title: 'Retrieval Method',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'notes',
      title: 'Notes',
      type: 'text',
      validation: (Rule) => Rule.required(),
    }),
  ],
  preview: {
    select: { title: 'title', subtitle: 'id' },
  },
})
