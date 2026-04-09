import 'package:flutter/material.dart';
import 'package:urdu_fonts/urdu_fonts.dart';

void main() => runApp(IqbalApp());

class IqbalApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Allama Iqbal Platform',
      theme: ThemeData(
        primaryColor: Color(0xFF1A237E),
        fontFamily: UrduFonts.notoNastaleeqUrdu,
      ),
      home: VerseOfTheDayScreen(),
    );
  }
}

class VerseOfTheDayScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Verse of the Day')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(
              'خودی کو کر بلند اتنا',
              style: TextStyle(
                fontFamily: UrduFonts.notoNastaleeqUrdu,
                fontSize: 32,
                color: Color(0xFF1A237E),
              ),
              textDirection: TextDirection.rtl,
            ),
            SizedBox(height: 16),
            Text(
              'Raise thyself to such heights...',
              style: TextStyle(fontSize: 18, color: Colors.black87),
              textAlign: TextAlign.left,
            ),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: () {
                // Navigate to detail
              },
              child: Text('Read More'),
            ),
          ],
        ),
      ),
    );
  }
}
