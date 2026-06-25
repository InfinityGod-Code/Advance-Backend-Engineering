import 'package:flutter/material.dart';
import '../../../models/tracking_event.dart';

class TrackingTimeline extends StatefulWidget {
  final List<TrackingEvent> events;

  const TrackingTimeline({super.key, required this.events});

  @override
  State<TrackingTimeline> createState() => _TrackingTimelineState();
}

class _TrackingTimelineState extends State<TrackingTimeline>
    with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final events = widget.events;
    if (events.isEmpty) {
      return const Center(child: Text('No tracking events'));
    }

    return ListView.builder(
      physics: const NeverScrollableScrollPhysics(),
      shrinkWrap: true,
      padding: const EdgeInsets.symmetric(horizontal: 16),
      itemCount: events.length,
      itemBuilder: (context, index) {
        final event = events[index];
        final isLast = index == events.length - 1;
        final isFirst = index == 0;
        final isCurrent = isLast;
        final nextEvent = isLast ? null : events[index + 1];

        return _TimelineItem(
          event: event,
          isFirst: isFirst,
          isLast: isLast,
          isCurrent: isCurrent,
          nextEvent: nextEvent,
          pulseValue: _pulseController,
        );
      },
    );
  }
}

class _TimelineItem extends StatelessWidget {
  final TrackingEvent event;
  final bool isFirst;
  final bool isLast;
  final bool isCurrent;
  final TrackingEvent? nextEvent;
  final Animation<double> pulseValue;

  const _TimelineItem({
    required this.event,
    required this.isFirst,
    required this.isLast,
    required this.isCurrent,
    this.nextEvent,
    required this.pulseValue,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SizedBox(
            width: 40,
            child: Column(
              children: [
                if (isFirst)
                  const SizedBox(height: 8)
                else
                  Expanded(
                    child: Container(
                      width: 2.5,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [
                            nextEvent?.status.color.withValues(alpha: 0.6) ??
                                event.status.color.withValues(alpha: 0.6),
                            event.status.color.withValues(alpha: 0.6),
                          ],
                        ),
                      ),
                    ),
                  ),
                if (isCurrent)
                  AnimatedBuilder(
                    animation: pulseValue,
                    builder: (context, child) {
                      final scale = 1.0 + (pulseValue.value * 0.5);
                      final opacity = 1.0 - (pulseValue.value * 0.4);
                      return SizedBox(
                        width: 32,
                        height: 32,
                        child: Stack(
                          alignment: Alignment.center,
                          children: [
                            Transform.scale(
                              scale: scale,
                              child: Container(
                                width: 32,
                                height: 32,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: event.status.color.withValues(
                                    alpha: 0.2 * opacity,
                                  ),
                                ),
                              ),
                            ),
                            Container(
                              width: 14,
                              height: 14,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: event.status.color,
                                boxShadow: [
                                  BoxShadow(
                                    color: event.status.color.withValues(
                                      alpha: 0.4,
                                    ),
                                    blurRadius: 6,
                                    spreadRadius: 1,
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  )
                else
                  Container(
                    width: 14,
                    height: 14,
                    margin: const EdgeInsets.symmetric(vertical: 8),
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: event.status.color,
                      border: Border.all(
                        color: event.status.color.withValues(alpha: 0.3),
                        width: 3,
                      ),
                    ),
                  ),
                if (isLast)
                  const Expanded(child: SizedBox())
                else
                  Expanded(
                    child: Container(
                      width: 2.5,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [
                            event.status.color.withValues(alpha: 0.3),
                            (nextEvent?.status.color ?? event.status.color)
                                .withValues(alpha: 0.1),
                          ],
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Container(
              margin: const EdgeInsets.only(bottom: 8),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: theme.colorScheme.surface,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: isCurrent
                      ? event.status.color.withValues(alpha: 0.3)
                      : theme.colorScheme.outlineVariant.withValues(alpha: 0.2),
                ),
                boxShadow: [
                  BoxShadow(
                    color: isCurrent
                        ? event.status.color.withValues(alpha: 0.08)
                        : Colors.black.withValues(alpha: 0.04),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        event.status.icon,
                        size: 16,
                        color: event.status.color,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        event.status.label,
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: event.status.color,
                        ),
                      ),
                      const Spacer(),
                      Text(
                        _formatTime(event.timestamp),
                        style: TextStyle(
                          fontSize: 11,
                          color: theme.colorScheme.onSurfaceVariant,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    event.description,
                    style: TextStyle(
                      fontSize: 13,
                      color: theme.colorScheme.onSurface,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Icon(
                        Icons.location_on_outlined,
                        size: 12,
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                      const SizedBox(width: 4),
                      Expanded(
                        child: Text(
                          event.location,
                          style: TextStyle(
                            fontSize: 11,
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                  if (isCurrent)
                    Padding(
                      padding: const EdgeInsets.only(top: 10),
                      child: Row(
                        children: [
                          Icon(
                            Icons.circle,
                            size: 6,
                            color: event.status.color,
                          ),
                          const SizedBox(width: 6),
                          Text(
                            'Current update',
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                              color: event.status.color,
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _formatTime(DateTime dt) {
    final hour = dt.hour > 12 ? dt.hour - 12 : (dt.hour == 0 ? 12 : dt.hour);
    final ampm = dt.hour >= 12 ? 'PM' : 'AM';
    final months = [
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec',
    ];
    final day = dt.day;
    final minute = dt.minute.toString().padLeft(2, '0');
    return '$hour:$minute $ampm, ${months[dt.month - 1]} $day';
  }
}
