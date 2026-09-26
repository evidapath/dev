// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.university) by
// 05-sanity/generation/gen_schema_files.py. Regenerate rather than
// hand-editing if the JSON Schema changes -- keeps the two in lockstep.
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'university',
  title: 'University',
  type: 'document',
  fields: [
    defineField({
      name: 'id',
      title: 'Id',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'canonical_name',
      title: 'Canonical Name',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'aliases',
      title: 'Aliases',
      type: 'array',
      of: [{ type: 'string' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'institution_type',
      title: 'Institution Type',
      type: 'string',
      options: { list: ["public", "private-nonprofit", "private-forprofit", "joint-venture"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'country_ref',
      title: 'Country',
      type: 'reference',
      weak: true,
      to: [{ type: 'country' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'primary_city_ref',
      title: 'Primary City',
      type: 'reference',
      weak: true,
      to: [{ type: 'city' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'official_website',
      title: 'Official Website',
      type: 'url',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'source_refs',
      title: 'Sources',
      type: 'array',
      of: [{ type: 'reference', weak: true, to: [{ type: 'sourceRecord' }] }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'record_status',
      title: 'Record Status',
      type: 'string',
      options: { list: ["RESEARCHED", "STRUCTURED", "VERIFIED", "HUMAN_REVIEW", "APPROVED", "PUBLISHED"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'last_researched',
      title: 'Last Researched',
      type: 'string', // unresolved $ref: iso_date
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'last_verified',
      title: 'Last Verified',
      type: 'string',
    }),
    defineField({
      name: 'extension_metadata',
      title: 'Extension Metadata',
      type: 'extensionMetadata',
    }),
  ],
  preview: {
    select: { title: 'canonical_name', subtitle: 'id' },
  },
})
