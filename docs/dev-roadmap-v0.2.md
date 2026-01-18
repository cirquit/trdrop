# TRDrop 2.0 Complete Development Specification

## Project Overview

TRDrop 2.0 is a cross-platform video analysis tool for measuring real framerate, frametime, and detecting screen tearing in raw video footage from capture cards. The application prioritizes **memory efficiency**, **cross-platform compatibility**, and **maximum development velocity** while providing professional-grade analysis capabilities.

### Key Requirements

- **Cross-platform development**: Develop on macOS, deploy to Windows/Linux via GitHub Actions
- **Raw video format support**: Handle diverse capture card outputs without codec complexity
- **Memory efficiency**: Analyze hour-long 4K videos without excessive RAM usage
- **Interactive editor**: Frame-accurate seeking with instant analysis feedback
- **Flexible export**: Multiple output formats with customizable overlays
- **Extensible architecture**: Plugin system for custom analysis algorithms

------

## Technology Stack Decision Matrix

### **Core Technology Choices**

| Technology            | Chosen Solution              | Rationale                                                    |
| --------------------- | ---------------------------- | ------------------------------------------------------------ |
| **GUI Framework**     | PyQt6                        | Cross-platform native look, mature ecosystem, familiar Qt patterns |
| **Video Processing**  | PyAV (libav bindings)        | Direct libav access, universal format support, frame-level control |
| **Analysis Language** | Python + NumPy               | Rapid development, rich ecosystem, easy algorithm prototyping |
| **Deployment**        | PyInstaller + GitHub Actions | Automated cross-platform builds, single executable distribution |
| **Build System**      | GitHub Actions matrix builds | Zero-setup cross-compilation, automated releases             |

### **Key Architectural Decisions**

**PyAV over OpenCV**:

- **Format Support**: PyAV handles all raw capture card formats through libav
- **Memory Control**: Direct access to AVFrame objects, zero-copy operations where possible
- **Professional Export**: Full FFmpeg encoding capabilities for high-quality output

**Layered Architecture over Monolithic**:

- **Flexibility**: Swappable components for different use modes (interactive/batch/headless)
- **Testability**: Each layer can be mocked and tested independently
- **Extensibility**: Plugin system for custom analysis algorithms and export overlays

**Cache Analysis, Not Frames**:

- **Memory Efficiency**: Analysis results ~1KB per frame vs 33MB raw frame data
- **Single Pass Analysis**: Read each video frame exactly once during initial analysis
- **Fast Random Access**: O(1) analysis lookup, acceptable frame seek performance

------

## Use Case Analysis

### **Primary Use Cases**

**1. Gaming Performance Analysis**

- **Users**: Content creators, competitive gamers, hardware reviewers
- **Input**: Raw capture card footage (YUV444, RGB, various bit depths)
- **Output**: Frame-accurate FPS analysis, tear detection, comparison videos
- **Requirements**: High accuracy, professional presentation, multiple video comparison

**2. Interactive Video Editing/Analysis**

- **Users**: Technical analysts, quality assurance testers
- **Workflow**: Load videos → seek to problem areas → analyze locally → export findings
- **Requirements**: Responsive seeking, context-aware analysis, overlay customization

**3. Batch Processing**

- **Users**: Research teams, automated testing pipelines
- **Workflow**: Headless analysis of large video collections
- **Requirements**: Unattended operation, persistent results, scriptable interface

**4. Real-time Monitoring**

- **Users**: Live streaming analysis, quality monitoring
- **Workflow**: Continuous analysis of incoming video stream
- **Requirements**: Low latency, minimal memory footprint, streaming export

### **Key User Scenarios**

**Scenario A: Content Creator Workflow**

1. Load 3 raw capture videos (different hardware configurations)
2. Seek through timeline to find performance issues
3. Get instant FPS analysis at any seek position (requiring 120-frame context)
4. Export comparison video with analysis overlays
5. Generate CSV report for detailed analysis

**Scenario B: Competitive Analysis**

1. Load single high-framerate raw video
2. Frame-by-frame analysis to identify micro-stutters
3. Export cropped sequences showing specific performance issues
4. Custom overlay templates for consistent branding

------

## System Architecture

### **Layered Component Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                        PyQt6 GUI Layer                          │
│  ┌──────────────────┐ ┌──────────────────┐ ┌─────────────────┐ │
│  │   Main Window    │ │   Video Widgets  │ │  Analysis Views │ │
│  │   - File Menu    │ │   - Multi-video  │ │  - Charts       │ │
│  │   - Tool Bars    │ │   - Seeking      │ │  - Statistics   │ │
│  │   - Status       │ │   - Overlays     │ │  - Export UI    │ │
│  └──────────────────┘ └──────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Core Orchestration Layer                    │
│  ┌──────────────────┐ ┌──────────────────┐ ┌─────────────────┐ │
│  │ Analysis         │ │  Analysis Cache  │ │  Export Manager │ │
│  │ Orchestrator     │ │  Manager         │ │  - Composition  │ │
│  │ - Smart scheduling│ │  - Multi-tier    │ │  - Encoding     │ │
│  │ - Context mgmt   │ │  - Persistence   │ │  - Progress     │ │
│  └──────────────────┘ └──────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Processing Engine Layer                      │
│  ┌──────────────────┐ ┌──────────────────┐ ┌─────────────────┐ │
│  │  Video Source    │ │ Analysis Engine  │ │  Cache Store    │ │
│  │  Abstraction     │ │  - Algorithms    │ │  Abstraction    │ │
│  │  - PyAV wrapper  │ │  - Context mgmt  │ │  - Multi-backend│ │
│  │  - Format detect │ │  - State recon   │ │  - Persistence  │ │
│  └──────────────────┘ └──────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                       PyAV Media Layer                          │
│                     (libavformat/libavcodec)                    │
└─────────────────────────────────────────────────────────────────┘
```

### **Core Component Specifications**

#### **Video Source Abstraction**

```python
class VideoSource(ABC):
    """Abstract interface for video access"""

    @abstractmethod
    def seek_to_frame(self, index: int) -> Frame:
        """Random access to specific frame"""
        pass

    @abstractmethod
    def get_frame_range(self, start: int, end: int) -> Iterator[Frame]:
        """Sequential access to frame range"""
        pass

    @abstractmethod
    def get_metadata(self) -> VideoMetadata:
        """Video properties (fps, resolution, format)"""
        pass

    @abstractmethod
    def supports_random_access(self) -> bool:
        """Whether seeking is supported"""
        pass

class PyAVVideoSource(VideoSource):
    """PyAV implementation for raw format support"""

    def __init__(self, path: str, format_hint: str = None):
        self.container = av.open(path, format=format_hint)
        self.stream = self.container.streams.video[0]

    def seek_to_frame(self, index: int) -> Frame:
        timestamp = index / self.stream.average_rate
        self.container.seek(int(timestamp * av.time_base.AV_TIME_BASE))
        packet = next(self.container.demux(video=0))
        frame = next(packet.decode())
        return frame.to_ndarray(format='rgb24')
```

#### **Analysis Cache Abstraction**

```python
class AnalysisStore(ABC):
    """Abstract interface for analysis result storage"""

    @abstractmethod
    def get_analysis(self, frame_index: int) -> Optional[AnalysisResult]:
        """Retrieve analysis for specific frame"""
        pass

    @abstractmethod
    def set_analysis(self, frame_index: int, result: AnalysisResult) -> None:
        """Store analysis result"""
        pass

    @abstractmethod
    def get_range(self, start: int, end: int) -> Dict[int, AnalysisResult]:
        """Batch retrieval for frame range"""
        pass

    @abstractmethod
    def has_complete_range(self, start: int, end: int) -> bool:
        """Check if range is fully analyzed"""
        pass

class CompositeStore(AnalysisStore):
    """Multi-tier cache implementation"""

    def __init__(self, l1_store: AnalysisStore, l2_store: AnalysisStore):
        self.l1 = l1_store  # Fast memory cache
        self.l2 = l2_store  # Persistent storage

    def get_analysis(self, frame_index: int) -> Optional[AnalysisResult]:
        # Check L1 cache first
        result = self.l1.get_analysis(frame_index)
        if result is not None:
            return result

        # Fall back to L2 cache
        result = self.l2.get_analysis(frame_index)
        if result is not None:
            self.l1.set_analysis(frame_index, result)  # Promote to L1

        return result
```

#### **Analysis Engine (Stateless)**

```python
class AnalysisEngine:
    """Pure function analysis processor"""

    def __init__(self):
        self.algorithms = {
            'fps_calculation': FPSAnalyzer(),
            'tear_detection': TearDetector(),
            'frame_difference': FrameDiffAnalyzer()
        }

    def analyze_frame_with_context(self,
                                   target_frame: int,
                                   context_frames: List[Frame]) -> AnalysisResult:
        """Analyze single frame with required context"""

        result = AnalysisResult(frame_index=target_frame)

        for name, analyzer in self.algorithms.items():
            analysis = analyzer.process(target_frame, context_frames)
            result.add_analysis(name, analysis)

        return result

    def get_required_context(self, algorithm: str) -> ContextRequirements:
        """Get context requirements for specific algorithm"""
        return self.algorithms[algorithm].get_context_requirements()

class ContextRequirements:
    def __init__(self, lookback: int, lookahead: int = 0):
        self.lookback = lookback    # Frames needed before target
        self.lookahead = lookahead  # Frames needed after target
```

#### **Smart Orchestration Layer**

```python
class AnalysisOrchestrator:
    """Intelligent analysis scheduling and coordination"""

    def __init__(self,
                 video_source: VideoSource,
                 cache: AnalysisStore,
                 engine: AnalysisEngine):
        self.video_source = video_source
        self.cache = cache
        self.engine = engine
        self.background_scheduler = BackgroundScheduler()

    async def get_analysis_at(self, frame_index: int) -> AnalysisResult:
        """Get analysis for frame, computing if necessary"""

        # Check cache first
        cached_result = self.cache.get_analysis(frame_index)
        if cached_result is not None:
            return cached_result

        # Determine context requirements
        max_context = max(self.engine.get_required_context(alg).lookback
                         for alg in self.engine.algorithms.keys())

        context_start = max(0, frame_index - max_context)
        context_end = frame_index + 1

        # Check if we can do quick analysis
        missing_frames = self._get_missing_frames(context_start, context_end)

        if len(missing_frames) < QUICK_ANALYSIS_THRESHOLD:
            # Immediate analysis for responsive UI
            return await self._analyze_immediately(frame_index, missing_frames)
        else:
            # Background analysis for large context
            self.background_scheduler.schedule_analysis(
                context_start, context_end, priority=HIGH
            )
            return self._get_estimated_result(frame_index)

    async def _analyze_immediately(self,
                                   target_frame: int,
                                   missing_range: range) -> AnalysisResult:
        """Fast analysis for small context requirements"""

        # Read required frames
        context_frames = []
        for frame_idx in missing_range:
            frame = self.video_source.seek_to_frame(frame_idx)
            context_frames.append(frame)

        # Analyze and cache
        result = self.engine.analyze_frame_with_context(target_frame, context_frames)
        self.cache.set_analysis(target_frame, result)

        return result
```

### **Data Flow Patterns**

#### **Initial Analysis (Batch Mode)**

```
Sequential Video Processing:
1. Open video containers (PyAV)
2. Read frames sequentially (optimal I/O)
3. Analyze with full context (120+ frames)
4. Store results in persistent cache
5. Close containers

Memory Usage: ~100MB working frames + ~1MB results per 10K frames
Storage: Analysis results only (~100KB per minute of video)
```

#### **Interactive Seeking**

```
User Seeks to Frame N:
1. Check cache for frame N analysis
2. If cached: return immediately (O(1) lookup)
3. If missing: determine context requirements
4. If small context: immediate analysis (<50ms)
5. If large context: background analysis + estimated result
6. Update UI when background analysis completes

Memory Usage: ~33MB single frame + ~1KB analysis lookup
Performance: <100ms for cache hits, <500ms for cache misses
```

#### **Export Processing**

```
Multi-Video Export:
1. Open all source videos
2. Sequential frame reading (re-read, memory efficient)
3. Use cached analysis (no re-computation)
4. Compose multi-video layout
5. Render overlays from analysis data
6. Encode to output format

Memory Usage: ~100MB composition frames + ~1KB analysis per frame
Performance: Real-time encoding speed, no analysis overhead
```

------

## Development Timeline & Milestones

### **Phase 0: Foundation Validation (Critical Path)**

#### **Milestone 0.1: Cross-Platform Compatibility Verification**

**Goal**: Prove PyQt6 + PyAV works reliably across all target platforms

**Critical Tests**:

- [ ] Basic PyQt6 application runs on Windows/Mac/Linux via GitHub Actions
- [ ] PyAV can load and decode various raw video formats on all platforms
- [ ] GitHub Actions can build and package executables for all platforms
- [ ] Font rendering, DPI scaling, and native OS integration work consistently

**Deliverables**:

- [ ] Minimal test application with PyQt6 video widget
- [ ] PyAV format compatibility test suite
- [ ] Complete GitHub Actions workflow for cross-platform builds
- [ ] Cross-platform behavior documentation and issue mitigation

**Success Criteria**:

- Same application works on fresh Windows 10/11, macOS 12+, Ubuntu 20.04+
- No major visual differences between platforms
- Automated builds succeed 100% of the time
- Raw video formats load correctly on all platforms

#### **Milestone 0.2: Architecture Proof of Concept**

**Goal**: Validate core architectural patterns before feature development

**Critical Tests**:

- [ ] Video source abstraction works with PyAV backend
- [ ] Analysis cache layer provides expected performance characteristics
- [ ] Analysis engine can process frames with context requirements
- [ ] Orchestration layer can manage async analysis requests
- [ ] Memory usage stays bounded during extended operation

**Deliverables**:

- [ ] Working implementation of all core abstractions
- [ ] End-to-end pipeline: load video → analyze → cache → retrieve
- [ ] Memory profiling and performance benchmarks
- [ ] Component integration tests

**Success Criteria**:

- Can analyze 1000+ frames without memory leaks
- Cache lookup performance <1ms for analysis results
- Context-aware analysis produces correct results
- Architecture scales to multi-video scenarios

#### **Milestone 0.3: Algorithm Implementation & Testing**

**Goal**: Implement core analysis algorithms with synthetic test data

**Critical Tests**:

- [ ] Frame difference calculation accuracy
- [ ] Tear detection with known synthetic patterns
- [ ] FPS calculation with controlled frame timing
- [ ] Context window handling (120+ frame lookback)
- [ ] State reconstruction for random seeking

**Deliverables**:

- [ ] Complete analysis algorithm implementations
- [ ] Synthetic test data generator for controlled scenarios
- [ ] Algorithm accuracy validation framework
- [ ] Performance benchmarks for analysis operations

**Success Criteria**:

- > 95% accuracy on synthetic test patterns

- Analysis performance >30fps on development hardware

- Context reconstruction works for arbitrary seek positions

- Algorithms handle edge cases gracefully

### **Phase 1: Core Application (MVP)**

#### **Milestone 1.1: Basic Video Analysis Application**

**Goal**: Working application with fundamental analysis capabilities

**Features**:

- [ ] Load single raw video file with format auto-detection
- [ ] Basic timeline scrubbing with frame-accurate seeking
- [ ] Real-time analysis result display (FPS, tears, frame difference)
- [ ] Analysis cache with persistence between sessions
- [ ] Basic CSV export of analysis results

**Deliverables**:

- [ ] Complete PyQt6 application with video playback
- [ ] Analysis orchestration with background processing
- [ ] Persistent analysis cache (SQLite backend)
- [ ] Basic export functionality
- [ ] User documentation and help system

**Success Criteria**:

- Can analyze 10+ minute videos without performance issues
- Seeking response time <200ms for cached analysis
- Analysis accuracy validated against manual verification
- Application feels responsive during heavy processing

#### **Milestone 1.2: Multi-Video Comparison**

**Goal**: Support simultaneous analysis of multiple videos

**Features**:

- [ ] Load and synchronize multiple raw video files
- [ ] Side-by-side video comparison display
- [ ] Synchronized seeking across all loaded videos
- [ ] Comparative analysis (cross-video metrics)
- [ ] Multi-video export with layout options

**Deliverables**:

- [ ] Multi-video UI layout and controls
- [ ] Synchronized video container management
- [ ] Cross-video analysis algorithms
- [ ] Layout composition for export
- [ ] Performance optimization for multiple video streams

**Success Criteria**:

- Can handle 3+ simultaneous 4K videos
- Synchronized seeking maintains frame accuracy
- Memory usage scales linearly with video count
- Export quality matches professional standards

### **Phase 2: Advanced Features & Polish**

#### **Milestone 2.1: Advanced Analysis Features**

**Goal**: Professional-grade analysis capabilities

**Features**:

- [ ] Advanced tear detection with sensitivity controls
- [ ] Frametime analysis and visualization
- [ ] Statistical analysis and trend detection
- [ ] User-configurable analysis parameters
- [ ] Custom analysis region selection

**Deliverables**:

- [ ] Enhanced analysis algorithm suite
- [ ] Interactive analysis parameter controls
- [ ] Advanced visualization components (charts, heatmaps)
- [ ] Statistical reporting and trend analysis
- [ ] Algorithm performance optimization

**Success Criteria**:

- Analysis accuracy competitive with professional tools
- Advanced features are discoverable and intuitive
- Parameter changes provide immediate visual feedback
- Performance scales to long-form content (hours)

#### **Milestone 2.2: Professional Export System**

**Goal**: Comprehensive export capabilities with customization

**Features**:

- [ ] Template-based overlay system
- [ ] Custom overlay design tools
- [ ] Batch export processing
- [ ] Multiple output formats and quality settings
- [ ] Progress tracking and export queue management

**Deliverables**:

- [ ] Complete overlay rendering system
- [ ] Template editor with live preview
- [ ] Batch processing workflow
- [ ] Export quality validation and optimization
- [ ] User template sharing system

**Success Criteria**:

- Export quality indistinguishable from manual video editing
- Template system enables extensive customization
- Batch processing handles large workloads efficiently
- Export performance competitive with dedicated video tools

### **Phase 3: Distribution & Community**

#### **Milestone 3.1: Production Release**

**Goal**: Stable, distributable application ready for end users

**Features**:

- [ ] Comprehensive error handling and recovery
- [ ] Auto-update system for seamless updates
- [ ] Crash reporting and telemetry (opt-in)
- [ ] Extensive help documentation and tutorials
- [ ] Performance monitoring and optimization

**Deliverables**:

- [ ] Production-ready application builds
- [ ] Automated distribution pipeline
- [ ] Comprehensive user documentation
- [ ] Support and troubleshooting resources
- [ ] Community feedback integration

**Success Criteria**:

- <0.1% crash rate in normal usage scenarios
- Update system works reliably across all platforms
- New users can complete basic analysis workflow in <10 minutes
- Application performs competitively with existing tools

------

## Testing Strategy & Validation Framework

### **Unit Testing Requirements**

#### **Component-Level Tests**

```python
class TestVideoSource:
    def test_format_detection(self):
        """Test automatic format detection for various raw formats"""
        test_cases = [
            ('yuv444_1080p.raw', 'rawvideo', 'yuv444p'),
            ('rgb24_720p.raw', 'rawvideo', 'rgb24'),
            ('yuv422_10bit.raw', 'rawvideo', 'yuv422p10le')
        ]

        for file_path, expected_format, expected_pix_fmt in test_cases:
            source = PyAVVideoSource(file_path)
            assert source.detected_format == expected_format
            assert source.pixel_format == expected_pix_fmt

class TestAnalysisCache:
    def test_cache_persistence(self):
        """Test that analysis results survive application restart"""
        cache = SQLiteStore('test.db')

        # Store analysis result
        result = AnalysisResult(frame_index=100, fps=59.8, tears=[])
        cache.set_analysis(100, result)

        # Simulate restart
        cache.close()
        cache = SQLiteStore('test.db')

        # Verify persistence
        retrieved = cache.get_analysis(100)
        assert retrieved.fps == 59.8

    def test_cache_performance(self):
        """Test cache lookup performance at scale"""
        cache = InMemoryStore()

        # Populate cache with realistic data
        for i in range(10000):
            result = AnalysisResult(frame_index=i, fps=60.0)
            cache.set_analysis(i, result)

        # Measure lookup performance
        start_time = time.time()
        for i in range(1000):
            cache.get_analysis(random.randint(0, 9999))
        lookup_time = (time.time() - start_time) / 1000

        assert lookup_time < 0.001  # <1ms per lookup
```

#### **Integration Tests**

```python
class TestAnalysisOrchestrator:
    def test_context_reconstruction(self):
        """Test that seeking provides accurate context-aware analysis"""
        orchestrator = self.setup_test_orchestrator()

        # Analyze video sequentially (ground truth)
        sequential_results = {}
        for frame_idx in range(1000):
            result = orchestrator.analyze_sequential(frame_idx)
            sequential_results[frame_idx] = result

        # Test random seeking produces same results
        for _ in range(100):
            random_frame = random.randint(120, 999)  # Ensure context available
            seek_result = orchestrator.get_analysis_at(random_frame)

            assert abs(seek_result.fps - sequential_results[random_frame].fps) < 0.1
            assert seek_result.tears == sequential_results[random_frame].tears

    def test_memory_usage_bounds(self):
        """Test that memory usage stays bounded during extended operation"""
        orchestrator = self.setup_test_orchestrator()
        initial_memory = psutil.Process().memory_info().rss

        # Simulate extended random seeking
        for _ in range(1000):
            frame_idx = random.randint(0, 10000)
            orchestrator.get_analysis_at(frame_idx)

        final_memory = psutil.Process().memory_info().rss
        memory_growth = final_memory - initial_memory

        assert memory_growth < 100 * 1024 * 1024  # <100MB growth
```

### **Synthetic Test Data Generation**

#### **Controlled Test Scenarios**

```python
class TestDataGenerator:
    def generate_constant_fps_video(self, fps: float, duration: int) -> str:
        """Generate video with perfect frame timing"""
        frames = []
        for i in range(duration * fps):
            frame = self.create_test_frame(1920, 1080, frame_number=i)
            frames.append(frame)
        return self.save_raw_video(frames, fps)

    def generate_frame_drops(self, base_fps: float, drop_pattern: List[int]) -> str:
        """Generate video with specific frame drop pattern"""
        frames = []
        frame_counter = 0

        for pattern_frame in drop_pattern:
            if pattern_frame == 1:  # Normal frame
                frame = self.create_test_frame(1920, 1080, frame_number=frame_counter)
                frames.append(frame)
                frame_counter += 1
            else:  # Dropped frame (duplicate previous)
                if frames:
                    frames.append(frames[-1])  # Duplicate last frame

        return self.save_raw_video(frames, base_fps)

    def generate_synthetic_tears(self, tear_positions: List[Tuple[int, int]]) -> str:
        """Generate video with artificial screen tearing at specified positions"""
        frames = []

        for frame_idx in range(1000):
            frame = self.create_test_frame(1920, 1080)

            # Add tears at specified positions
            for tear_frame, tear_y in tear_positions:
                if frame_idx == tear_frame:
                    frame = self.add_synthetic_tear(frame, tear_y)

            frames.append(frame)

        return self.save_raw_video(frames, 60.0)
```

### **Performance Benchmarking**

#### **Baseline Performance Tests**

```python
class PerformanceBenchmarks:
    def benchmark_analysis_speed(self):
        """Measure analysis throughput"""
        video_path = self.get_test_video_4k_60fps()
        orchestrator = AnalysisOrchestrator(video_path)

        start_time = time.time()
        frame_count = 0

        for frame_idx in range(0, 1800, 30):  # Sample every 30 frames
            orchestrator.get_analysis_at(frame_idx)
            frame_count += 1

        elapsed_time = time.time() - start_time
        fps_throughput = frame_count / elapsed_time

        assert fps_throughput > 30  # Must process >30fps worth of analysis

    def benchmark_memory_efficiency(self):
        """Measure memory usage scaling"""
        memory_samples = []

        for video_length in [1, 5, 10, 30]:  # minutes
            video_path = self.generate_test_video(length_minutes=video_length)
            orchestrator = AnalysisOrchestrator(video_path)

            # Trigger full analysis
            orchestrator.analyze_full_video()

            memory_usage = psutil.Process().memory_info().rss
            memory_samples.append((video_length, memory_usage))

        # Memory should scale sub-linearly with video length
        memory_per_minute = [mem / length for length, mem in memory_samples]
        assert max(memory_per_minute) / min(memory_per_minute) < 2.0
```

------

## Risk Mitigation & Contingency Plans

### **Technical Risks**

**Risk**: PyQt6 cross-platform inconsistencies

- **Mitigation**: Early cross-platform testing in Phase 0
- **Contingency**: Use a different cross-platform framework, maybe think about a C++ library and calling from a simple GUI toolkit, whichever language fits best for cross-platform

**Risk**: PyAV format compatibility issues

- **Mitigation**: Comprehensive format testing with real capture card footage
- **Contingency**: Hybrid PyAV + OpenCV approach for problematic formats

**Risk**: Memory usage scaling problems

- **Mitigation**: Continuous memory profiling and benchmarking
- **Contingency**: Implement frame caching for small videos, streaming for large videos

**Risk**: Analysis accuracy insufficient

- **Mitigation**: Extensive validation against known test patterns
- **Contingency**: Algorithm improvement iterations, possibly ML-based approaches

### **Project Risks**

**Risk**: Development timeline overruns

- **Mitigation**: Phased development with working software at each milestone
- **Contingency**: Reduce feature scope, focus on core MVP functionality

**Risk**: Cross-platform build complexity

- **Mitigation**: GitHub Actions setup and testing in Phase 0
- **Contingency**: Single-platform release initially, add platforms iteratively

**Risk**: User adoption challenges

- **Mitigation**: Early user feedback integration, familiar UI patterns
- **Contingency**: Community engagement, tutorial content, format migration tools

------

## Getting Started Checklist

### **Development Environment Setup**

- [ ] Install Python 3.11+ with PyQt6 and PyAV dependencies
- [ ] Set up cross-platform testing with virtual machines or containers
- [ ] Configure GitHub repository with Actions workflow templates
- [ ] Create initial project structure with core abstraction interfaces
- [ ] Set up development tooling (linting, testing, profiling)

### **Phase 0 Immediate Tasks**

1. **Week 1**: Cross-platform PyQt6 + PyAV compatibility testing
2. **Week 2**: Core architecture implementation and validation
3. **Week 3**: Synthetic test data generation and algorithm development
4. **Week 4**: Performance benchmarking and optimization

### **Success Validation**

- All Phase 0 tests pass on Windows, macOS, and Linux
- Core architecture handles realistic video analysis scenarios
- Memory usage and performance meet established benchmarks
- GitHub Actions reliably produce distributable executables

This specification provides the complete foundation for developing TRDrop 2.0 with confidence in the architectural decisions, clear milestones for progress tracking, and comprehensive testing to ensure success.
