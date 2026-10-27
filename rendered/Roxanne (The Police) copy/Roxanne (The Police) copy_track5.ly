\version "2.10.33"

        \version "2.24.4"
        #(set-global-staff-size 14)
        #(ly:set-option 'crop #t)
        #(set-paper-size "a4")    % Set the physical page size
        \paper {
            top-margin = 10\mm        % Adjust margins to prevent clipping
            bottom-margin = 10\mm
            left-margin = 15\mm
            line-width = 180\mm       % Must match the layout's expectations
        }
    
        \layout {
            ragged-right = ##f
            \context {
                \Score
                % This forces LilyPond to allow breaks even if it thinks they look bad
                \override SpacingSpanner.strict-grace-spacing = ##t
                \override SpacingSpanner.strict-note-spacing = ##t
                forbidBreakBetweenBarLines = ##f
                override BarLine.transparent = ##f
                % This tells LilyPond "even if the math is wrong, draw the bar and allow a break"
                barCheckSynchronize = ##t 
            }
        }
    \header { title = "Untitled" composer = "" opus = "" } { { } { <c'' dis''>8 r8 \times 2/3 {<d'' f''>\breve }} { c''4 r8 <d'' dis''>8 r8 \times 4/5 {<c'' f''>\breve }} { <c'' ais''>8 r8 \times 4/5 {<d'' g''>\breve }} { <c'' a''>8 r8 \times 4/5 {<d'' f''>\breve }} { <dis'' ais''>8 r8 \times 2/3 {<c'' a''>\breve }} { } { <c'' dis''>8 r8 \times 4/5 {<d'' f''>\breve }} { <d'' ais''>8 r8 \times 4/5 {<c'' a''>\breve }} { <c'' ais''>8 r8 \times 4/5 {<d'' g''>\breve }} { <dis'' ais''>8 r8 \times 4/5 {<d'' f''>\breve }} { <dis'' ais''>8 r8 \times 4/5 {<c'' a''>\breve }} { <c'' ais''>8 r8 \times 4/5 {<d'' g''>\breve }} { <dis'' ais''>8 r8 \times 4/5 {<d'' f''>\breve }} { <d'' ais''>8 r8 \times 4/5 {<c'' a''>\breve }} { <c'' ais''>8 r8 \times 4/5 {<d'' g''>\breve }} { <dis'' ais''>8 r8 \times 4/5 {<d'' f''>\breve }} { <d'' ais''>8 r8 \times 4/5 {<c'' a''>\breve }} { <c'' ais''>8 r8 \times 4/5 {<d'' g''>\breve }} { <dis'' ais''>8 r8 \times 4/5 {<d'' f''>\breve }} { <dis'' ais''>8 r8 \times 4/5 {<c'' a''>\breve }} { <c'' ais''>8 r8 \times 4/5 {<d'' g''>\breve }} { <c'' dis''>8 r8 \times 4/5 {<d'' f''>\breve }} { <d'' ais''>8 r8 \times 4/5 {<c'' a''>\breve }} { <c'' ais''>8 r8 <d'' g''>8 r4 r4 } }