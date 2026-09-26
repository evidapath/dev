// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.campus) by
// 05-sanity/generation/gen_schema_files.py. Regenerate rather than
// hand-editing if the JSON Schema changes -- keeps the two in lockstep.
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'campus',
  title: 'Campus',
  type: 'document',
  fields: [
    defineField({
      name: 'id',
      title: 'Id',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'university_ref',
      title: 'University',
      type: 'reference',
      to: [{ type: 'university' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'name',
      title: 'Name',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'city_ref',
      title: 'City',
      type: 'reference',
      to: [{ type: 'city' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'country_ref',
      title: 'Country',
      type: 'reference',
      to: [{ type: 'country' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'is_primary',
      title: 'Is Primary',
      type: 'boolean',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'official_url',
      title: 'Official Url',
      type: 'url',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'extension_metadata',
      title: 'Extension Metadata',
      type: 'extensionMetadata',
    }),
  ],
  preview: {
    select: { title: 'name', subtitle: 'id' },
  },
})
