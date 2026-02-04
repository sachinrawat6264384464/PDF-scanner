# Implementation Plan: Bharat Suraksha AI Suite

## Overview

This implementation plan breaks down the Bharat Suraksha AI Suite into discrete, manageable coding tasks. The platform will be built using Python for backend services and AI/ML components, and TypeScript/React for the frontend. The implementation follows a phased approach, starting with core infrastructure, then building VoiceShield AI, followed by NyayaMitra AI, and finally integrating all components.

## Technology Stack

- **Backend**: Python 3.10+ with FastAPI
- **Frontend**: TypeScript with React/Next.js
- **Database**: MongoDB
- **Cache**: Redis
- **Queue**: AWS SQS
- **Storage**: AWS S3
- **AI/ML**: AWS SageMaker, Hugging Face Transformers
- **Vector DB**: FAISS/OpenSearch

## Tasks

- [ ] 1. Set up project structure and development environment
  - Create monorepo structure with backend and frontend directories
  - Set up Python virtual environment and install core dependencies (FastAPI, pymongo, boto3, redis)
  - Set up TypeScript/React project with Next.js
  - Configure ESLint, Prettier, and pre-commit hooks
  - Create Docker Compose file for local development (MongoDB, Redis)
  - Set up environment variable management (.env files)
  - _Requirements: All (foundational)_

- [ ] 2. Implement authentication and user management
  - [ ] 2.1 Create User data model and MongoDB schema
    - Define User model with all fields (email, phone, password_hash, settings, usage_stats)
    - Create MongoDB indexes for email and phone
    - Implement password hashing using bcrypt
    - _Requirements: 1.1, 1.4_
  
  - [ ]* 2.2 Write property test for user registration encryption
    - **Property 1: User Registration Creates Encrypted Accounts**
    - **Validates: Requirements 1.1, 1.4**
  
  - [ ] 2.3 Implement registration API endpoint
    - Create POST /api/v1/auth/register endpoint
    - Validate email, phone, and password complexity
    - Hash password and create user record
    - Return success response with user ID
    - _Requirements: 1.1, 1.4_
  
  - [ ] 2.4 Implement login and JWT token generation
    - Create POST /api/v1/auth/login endpoint
    - Verify credentials against database
    - Generate JWT token with expiration
    - Store session in Redis
    - _Requirements: 1.2_
  
  - [ ]* 2.5 Write property test for authentication round-trip
    - **Property 2: Authentication Round-Trip**
    - **Validates: Requirements 1.2, 1.3**
  
  - [ ] 2.6 Implement JWT token validation middleware
    - Create authentication middleware for protected routes
    - Verify JWT signature and expiration
    - Extract user ID from token
    - Handle expired tokens with 401 response
    - _Requirements: 1.3_
  
  - [ ] 2.7 Implement password reset flow
    - Create POST /api/v1/auth/reset-password endpoint for request
    - Generate secure reset token with expiration
    - Send reset email (mock for now, integrate later)
    - Create PUT /api/v1/auth/reset-password endpoint for completion
    - _Requirements: 1.5_
  
  - [ ]* 2.8 Write unit tests for authentication edge cases
    - Test invalid email formats
    - Test weak passwords
    - Test duplicate registration
    - Test invalid credentials
    - _Requirements: 1.1, 1.2, 1.4_


- [ ] 3. Implement audio upload and storage
  - [ ] 3.1 Create Audio Record data model
    - Define AudioRecord model with file metadata
    - Create MongoDB indexes for audio_id and user_id
    - _Requirements: 2.1, 2.3_
  
  - [ ] 3.2 Implement file upload API endpoint
    - Create POST /api/v1/audio/upload endpoint with multipart/form-data
    - Validate file format (MP3, WAV, M4A, OGG)
    - Validate file size (max 50MB)
    - Generate unique audio_id
    - _Requirements: 2.1, 2.2_
  
  - [ ]* 3.3 Write property test for file format validation
    - **Property 7: File Format Validation**
    - **Validates: Requirements 2.1**
  
  - [ ] 3.4 Implement S3 upload with encryption
    - Configure AWS S3 client with KMS encryption
    - Upload audio file to S3 with AES-256 encryption
    - Store S3 key and encryption metadata in database
    - _Requirements: 2.3, 13.1_
  
  - [ ]* 3.5 Write property test for audio file encryption
    - **Property 4: Audio File Encryption**
    - **Validates: Requirements 2.3, 13.1**
  
  - [ ] 3.6 Implement auto-delete scheduling
    - Add auto_delete_at field calculation (upload_time + 24 hours)
    - Create background job to delete expired files
    - _Requirements: 2.5_
  
  - [ ]* 3.7 Write property test for auto-delete scheduling
    - **Property 8: Auto-Delete Scheduling**
    - **Validates: Requirements 2.5**

- [ ] 4. Implement audio processing job queue
  - [ ] 4.1 Create Analysis Job data model
    - Define AnalysisJob model with status tracking
    - Create MongoDB indexes for job_id and status
    - _Requirements: 2.4_
  
  - [ ] 4.2 Implement SQS queue integration
    - Configure AWS SQS client
    - Create function to publish job to queue
    - Include job_id, audio_id, user_id in message
    - _Requirements: 2.4_
  
  - [ ] 4.3 Implement job status tracking API
    - Create GET /api/v1/audio/status/{job_id} endpoint
    - Return current job status and progress
    - Implement WebSocket for real-time updates
    - _Requirements: 2.4_
  
  - [ ]* 4.4 Write property test for processing status updates
    - **Property 9: Processing Status Updates**
    - **Validates: Requirements 2.4**

- [ ] 5. Checkpoint - Ensure authentication and upload work
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement audio quality assessment
  - [ ] 6.1 Create audio quality validation module
    - Implement function to extract audio metadata (sample rate, bit rate)
    - Calculate noise level using signal processing
    - Generate quality score (0-1)
    - _Requirements: 17.1_
  
  - [ ]* 6.2 Write property test for audio quality validation
    - **Property 10: Audio Quality Validation**
    - **Validates: Requirements 17.1, 17.2**
  
  - [ ] 6.3 Implement noise reduction
    - Integrate noise reduction library (noisereduce or similar)
    - Apply noise reduction to low-quality audio
    - Verify quality improvement
    - _Requirements: 17.3_
  
  - [ ]* 6.4 Write property test for noise reduction
    - **Property 11: Noise Reduction Application**
    - **Validates: Requirements 17.3**

- [ ] 7. Implement speech-to-text transcription
  - [ ] 7.1 Set up Wav2Vec2/Whisper model
    - Download and configure multilingual transcription model
    - Create SageMaker endpoint or local inference setup
    - Test with sample Hindi, English, and Hinglish audio
    - _Requirements: 5.1, 5.2_
  
  - [ ] 7.2 Implement transcription service
    - Create function to call transcription model
    - Process audio in chunks if needed
    - Generate time-stamped transcript with speaker labels
    - Handle multiple languages (Hindi, English, Hinglish)
    - _Requirements: 5.1, 5.2, 5.3_
  
  - [ ]* 7.3 Write property test for transcription completeness
    - **Property 17: Transcription Completeness**
    - **Validates: Requirements 5.1, 5.2, 5.3**
  
  - [ ] 7.4 Implement transcript export functionality
    - Create function to export transcript as TXT
    - Create function to export transcript as PDF
    - _Requirements: 5.4_
  
  - [ ]* 7.5 Write property test for transcript export formats
    - **Property 18: Transcript Export Formats**
    - **Validates: Requirements 5.4**

- [ ] 8. Implement deepfake detection
  - [ ] 8.1 Set up deepfake detection model
    - Download or train deepfake classifier model
    - Create SageMaker endpoint or local inference setup
    - Test with sample real and synthetic voices
    - _Requirements: 3.1_
  
  - [ ] 8.2 Implement deepfake analysis service
    - Extract audio features (MFCCs, spectral features)
    - Call deepfake detection model
    - Generate deepfake score (0-100)
    - Classify as Real or AI-generated based on threshold (70%)
    - Calculate confidence level
    - _Requirements: 3.1, 3.2, 3.5_
  
  - [ ]* 8.3 Write property test for deepfake score generation
    - **Property 12: Deepfake Score Generation and Classification**
    - **Validates: Requirements 3.1, 3.2, 3.5**
  
  - [ ] 8.4 Implement multi-speaker deepfake analysis
    - Perform speaker diarization
    - Analyze each speaker separately
    - Generate per-speaker deepfake scores
    - _Requirements: 3.3_
  
  - [ ]* 8.5 Write property test for multi-speaker analysis
    - **Property 13: Multi-Speaker Deepfake Analysis**
    - **Validates: Requirements 3.3**

- [ ] 9. Implement scam intent classification
  - [ ] 9.1 Set up scam classification model
    - Fine-tune mBERT or IndicBERT on scam detection dataset
    - Create SageMaker endpoint or local inference setup
    - Define scam categories (OTP, police, bank fraud, etc.)
    - _Requirements: 4.1, 4.2_
  
  - [ ] 9.2 Implement scam analysis service
    - Preprocess transcript text
    - Call scam classification model
    - Generate scam scores per category
    - Identify primary scam category
    - Calculate overall scam score
    - _Requirements: 4.1, 4.2, 4.5_
  
  - [ ]* 9.3 Write property test for scam classification
    - **Property 14: Scam Classification Completeness**
    - **Validates: Requirements 4.1, 4.2, 4.5**
  
  - [ ] 9.4 Implement keyword detection
    - Define scam keyword patterns (OTP, UPI, bank, urgent, etc.)
    - Search transcript for keywords
    - Extract timestamps for each keyword occurrence
    - _Requirements: 4.3_
  
  - [ ]* 9.5 Write property test for keyword detection
    - **Property 15: Keyword Detection with Timestamps**
    - **Validates: Requirements 4.3**
  
  - [ ] 9.6 Implement suspicious segment identification
    - Analyze keyword density over time
    - Combine with scam scores
    - Identify time ranges with high risk
    - Assign risk levels (low/medium/high) to segments
    - _Requirements: 4.4_
  
  - [ ]* 9.7 Write property test for suspicious segments
    - **Property 16: Suspicious Segment Identification**
    - **Validates: Requirements 4.4**

- [ ] 10. Implement entity extraction
  - [ ] 10.1 Create entity extraction module
    - Implement regex patterns for phone numbers
    - Implement regex patterns for UPI IDs
    - Implement regex patterns for amounts and currency
    - Implement regex patterns for dates and times
    - Implement regex patterns for transaction references
    - Extract bank names using NER or pattern matching
    - _Requirements: 9.2_
  
  - [ ]* 10.2 Write property test for entity extraction
    - **Property 28: Complaint Draft Generation with Auto-Fill** (entity extraction part)
    - **Validates: Requirements 9.2**

- [ ] 11. Implement risk assessment and report generation
  - [ ] 11.1 Create Analysis Result data model
    - Define AnalysisResult model with all analysis sections
    - Create MongoDB indexes for job_id and user_id
    - _Requirements: 6.1_
  
  - [ ] 11.2 Implement severity level calculation
    - Define severity thresholds (Low < 30, Medium 30-60, High 60-85, Emergency > 85)
    - Calculate severity based on deepfake and scam scores
    - Handle emergency cases (deepfake > 80 AND scam > 50)
    - _Requirements: 6.2_
  
  - [ ]* 11.3 Write property test for severity calculation
    - **Property 20: Comprehensive Report Generation** (severity part)
    - **Validates: Requirements 6.2**
  
  - [ ] 11.4 Implement safety recommendations generator
    - Map scam categories to appropriate recommendations
    - Include emergency helpline numbers for high-risk cases
    - Generate actionable advice
    - _Requirements: 6.4_
  
  - [ ]* 11.5 Write property test for recommendations
    - **Property 20: Comprehensive Report Generation** (recommendations part)
    - **Validates: Requirements 6.4**
  
  - [ ] 11.6 Implement report compilation
    - Aggregate all analysis results
    - Create complete report structure
    - Store in MongoDB
    - _Requirements: 6.1_
  
  - [ ]* 11.7 Write property test for report generation
    - **Property 20: Comprehensive Report Generation**
    - **Validates: Requirements 6.1, 6.2, 6.4**
  
  - [ ] 11.8 Implement PDF report export
    - Create PDF generation function using ReportLab or similar
    - Include all report sections with formatting
    - _Requirements: 6.5_
  
  - [ ]* 11.9 Write property test for PDF export
    - **Property 22: Report PDF Export**
    - **Validates: Requirements 6.5**

- [ ] 12. Checkpoint - Ensure VoiceShield AI pipeline works end-to-end
  - Ensure all tests pass, ask the user if questions arise.


- [ ] 13. Implement audio processing orchestrator
  - [ ] 13.1 Create audio processing worker service
    - Set up SQS consumer to receive processing jobs
    - Implement job status updates (queued → processing → completed/failed)
    - Handle errors and retries with exponential backoff
    - _Requirements: 2.4_
  
  - [ ] 13.2 Implement complete processing pipeline
    - Orchestrate all stages: quality check → transcription → deepfake → scam → entity extraction → report
    - Handle stage failures gracefully
    - Update job status at each stage
    - Send emergency notifications for high-severity results
    - _Requirements: All VoiceShield requirements_
  
  - [ ]* 13.3 Write integration test for complete pipeline
    - Test end-to-end audio processing
    - Verify all stages complete successfully
    - Verify data consistency across stages
    - _Requirements: All VoiceShield requirements_

- [ ] 14. Implement timeline visualization data generation
  - [ ] 14.1 Create timeline data structure
    - Generate timeline segments with timestamps
    - Color-code segments by risk level (green/yellow/red)
    - Add keyword markers to timeline
    - Include duration for each segment
    - _Requirements: 7.1, 7.2, 7.4, 7.5_
  
  - [ ]* 14.2 Write property test for timeline visualization
    - **Property 23: Timeline Visualization Data Structure**
    - **Validates: Requirements 7.1, 7.2, 7.4, 7.5**
  
  - [ ] 14.3 Implement timeline-transcript mapping
    - Create function to extract transcript excerpt for time range
    - Ensure accurate mapping between timeline and transcript
    - _Requirements: 7.3_
  
  - [ ]* 14.4 Write property test for timeline-transcript mapping
    - **Property 24: Timeline-Transcript Mapping**
    - **Validates: Requirements 7.3**

- [ ] 15. Implement NyayaMitra AI - RAG system setup
  - [ ] 15.1 Set up vector database
    - Configure FAISS or OpenSearch
    - Create index for legal document embeddings
    - _Requirements: 8.2_
  
  - [ ] 15.2 Implement document ingestion pipeline
    - Collect legal documents (IPC sections, IT Act, cybercrime guidelines)
    - Preprocess and chunk documents (512 tokens)
    - Generate embeddings using multilingual model
    - Store embeddings in vector database with metadata
    - _Requirements: 8.2_
  
  - [ ] 15.3 Implement similarity search
    - Create function to generate query embeddings
    - Perform similarity search in vector database
    - Retrieve top-k relevant document chunks
    - Re-rank by relevance score
    - _Requirements: 8.2_

- [ ] 16. Implement NyayaMitra AI - Chatbot
  - [ ] 16.1 Create Chat Session data model
    - Define ChatSession model with messages and context
    - Create MongoDB indexes for session_id and user_id
    - _Requirements: 8.4_
  
  - [ ] 16.2 Implement chatbot API endpoint
    - Create POST /api/v1/legal/chat endpoint
    - Receive user query and session_id
    - Maintain conversation history
    - _Requirements: 8.1, 8.4_
  
  - [ ] 16.3 Implement RAG-based response generation
    - Generate query embedding
    - Retrieve relevant legal documents
    - Construct prompt with context and conversation history
    - Call LLM for response generation
    - Extract source citations
    - _Requirements: 8.1, 8.2, 8.5_
  
  - [ ]* 16.4 Write property test for chatbot language matching
    - **Property 25: Chatbot Response Language Matching**
    - **Validates: Requirements 8.1, 8.5, 16.3**
  
  - [ ]* 16.5 Write property test for conversation context
    - **Property 27: Conversation Context Preservation**
    - **Validates: Requirements 8.4**
  
  - [ ] 16.6 Implement auto-suggestion for detected scams
    - Map scam categories to legal actions
    - Generate action suggestions based on analysis results
    - Return suggestions with chatbot response
    - _Requirements: 8.3_
  
  - [ ]* 16.7 Write property test for auto-suggestions
    - **Property 26: Auto-Suggestion for Detected Scams**
    - **Validates: Requirements 8.3**

- [ ] 17. Implement complaint draft generation
  - [ ] 17.1 Create Complaint Draft data model
    - Define ComplaintDraft model with template and auto-filled fields
    - Create MongoDB indexes for complaint_id and user_id
    - _Requirements: 9.1_
  
  - [ ] 17.2 Create complaint templates
    - Design FIR template
    - Design Cybercrime complaint template
    - Design Bank dispute letter template
    - Design Consumer forum complaint template
    - _Requirements: 9.1_
  
  - [ ] 17.3 Implement complaint generation API
    - Create POST /api/v1/legal/generate-complaint endpoint
    - Receive complaint type and analysis_id
    - Retrieve analysis results and extract entities
    - Auto-fill template with extracted data
    - Store draft in database
    - _Requirements: 9.1, 9.2, 9.3_
  
  - [ ]* 17.4 Write property test for complaint auto-fill
    - **Property 28: Complaint Draft Generation with Auto-Fill**
    - **Validates: Requirements 9.1, 9.2, 9.3**
  
  - [ ] 17.5 Implement complaint editing and export
    - Create PUT /api/v1/legal/complaint/{id} endpoint for editing
    - Implement PDF export for complaints
    - Implement DOCX export for complaints
    - _Requirements: 9.4, 9.5_
  
  - [ ]* 17.6 Write property test for complaint editability
    - **Property 29: Complaint Draft Editability and Export**
    - **Validates: Requirements 9.4, 9.5**

- [ ] 18. Implement legal guidance system
  - [ ] 18.1 Create legal guidance content
    - Write step-by-step instructions for filing cybercrime complaints
    - Write step-by-step instructions for filing FIR
    - Write step-by-step instructions for bank disputes
    - Write step-by-step instructions for consumer complaints
    - Include relevant website links and helpline numbers
    - _Requirements: 10.1, 10.2, 10.3_
  
  - [ ] 18.2 Implement guidance API endpoint
    - Create GET /api/v1/legal/guidance/{type} endpoint
    - Return comprehensive guidance with all required information
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [ ]* 18.3 Write property test for legal guidance completeness
    - **Property 30: Comprehensive Legal Guidance**
    - **Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5**

- [ ] 19. Checkpoint - Ensure NyayaMitra AI works correctly
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 20. Implement user dashboard
  - [ ] 20.1 Implement scan history API
    - Create GET /api/v1/dashboard/scans endpoint
    - Return all user scans with status
    - Support pagination
    - _Requirements: 11.1, 11.2_
  
  - [ ]* 20.2 Write property test for scan history display
    - **Property 31: Scan History Display**
    - **Validates: Requirements 11.1, 11.2, 11.3**
  
  - [ ] 20.3 Implement scan filtering
    - Add query parameters for date, severity_level, scam_category
    - Filter scans based on criteria
    - _Requirements: 11.4_
  
  - [ ]* 20.4 Write property test for scan filtering
    - **Property 32: Scan Filtering**
    - **Validates: Requirements 11.4**
  
  - [ ] 20.5 Implement user statistics API
    - Create GET /api/v1/dashboard/statistics endpoint
    - Calculate total scans, high-risk detections, complaints generated
    - _Requirements: 11.5_
  
  - [ ]* 20.6 Write property test for statistics calculation
    - **Property 33: User Statistics Calculation**
    - **Validates: Requirements 11.5**

- [ ] 21. Implement complaint tracking
  - [ ] 21.1 Implement complaint tracking API
    - Create GET /api/v1/dashboard/complaints endpoint
    - Return all tracked complaints with status
    - Create PUT /api/v1/dashboard/complaints/{id} endpoint for status updates
    - _Requirements: 19.1, 19.2, 19.3_
  
  - [ ]* 21.2 Write property test for complaint tracking
    - **Property 45: Complaint Tracking Record Creation**
    - **Validates: Requirements 19.1, 19.2**
  
  - [ ]* 21.3 Write property test for complaint display
    - **Property 46: Complaint Dashboard Display**
    - **Validates: Requirements 19.3**
  
  - [ ] 21.4 Implement complaint follow-up reminders
    - Create background job to check pending complaints
    - Send reminders for complaints older than 7 days
    - _Requirements: 19.4_
  
  - [ ]* 21.5 Write property test for follow-up reminders
    - **Property 47: Complaint Follow-Up Reminders**
    - **Validates: Requirements 19.4**
  
  - [ ] 21.6 Implement acknowledgment attachment
    - Create POST /api/v1/dashboard/complaints/{id}/attachment endpoint
    - Store attachment in S3
    - Link to complaint record
    - _Requirements: 19.5_
  
  - [ ]* 21.7 Write property test for acknowledgment attachment
    - **Property 48: Complaint Acknowledgment Attachment**
    - **Validates: Requirements 19.5**

- [ ] 22. Implement admin analytics
  - [ ] 22.1 Create Admin Analytics data model
    - Define AdminAnalytics model with daily metrics
    - Create MongoDB indexes for date
    - _Requirements: 12.1_
  
  - [ ] 22.2 Implement analytics aggregation job
    - Create background job to aggregate daily metrics
    - Calculate total scans, fraud type distribution, common keywords
    - Calculate geographic distribution
    - Store in AdminAnalytics collection
    - _Requirements: 12.1, 12.2, 12.3_
  
  - [ ] 22.3 Implement admin analytics API
    - Create GET /api/v1/admin/analytics endpoint
    - Return aggregated analytics data
    - Support date range filtering
    - _Requirements: 12.1, 12.2, 12.3_
  
  - [ ]* 22.4 Write property test for analytics aggregation
    - **Property 34: Admin Analytics Aggregation**
    - **Validates: Requirements 12.1, 12.2, 12.3**
  
  - [ ] 22.5 Implement performance metrics calculation
    - Calculate average processing time from logs
    - Calculate API response times
    - Calculate error rates
    - _Requirements: 12.4_
  
  - [ ]* 22.6 Write property test for performance metrics
    - **Property 35: Performance Metrics Calculation**
    - **Validates: Requirements 12.4**
  
  - [ ] 22.7 Implement analytics CSV export
    - Create POST /api/v1/admin/export endpoint
    - Generate CSV with all analytics data
    - _Requirements: 12.5_
  
  - [ ]* 22.8 Write property test for CSV export
    - **Property 36: Analytics CSV Export**
    - **Validates: Requirements 12.5**

