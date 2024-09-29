using Accessibility;
using System;
using System.Collections.Generic;
using System.Diagnostics.Contracts;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace Tableaux.Wpf
{
    public record Operator
    {
        public required string Name { get; init; }
        public required string[] Keys { get; init; }
        public required char Code { get; init; }
    }

    public class TreeNode
    {
        public TreeNode? Parent;
        public required string Value;
        public List<TreeNode> Children = new();
        public bool IsClosed { get; set; }

        public bool IsWithinScope(string value)
        {
            Contract.Requires(value != null);
            return value.Equals(Value) || (Parent?.IsWithinScope(value) ?? false);
        }
    }

    public class Conjecture
    {
        // Premises
        public required List<string> Premises { get; init; }
        // Conclusions
        public required string Conclusion { get; init; }
    }

    public class Theorem
    {
        public required string Name { get; init; }
        public required string PatternIn { get; init; }
        public required string PatternOut { get; init; }
        public required bool IsEquivalence { get; init; }
    }

    public class TableauxHelper
    {
        private readonly char[] m_parentheses = { '(', ')' };
        private readonly char[] m_codes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'];
        private readonly List<Operator> m_operators = new List<Operator>([
            new()
                {
                    Name = "Conjunction",
                    Code = '∧',
                    Keys = ["\\land", "\\wedge", "&&"]
                },
            new()
                {
                    Name = "Disjunction",
                    Code = '∨',
                    Keys = ["\\lor", "\\vee", "||"]
                },
            new()
                {
                    Name = "Negation",
                    Code = '¬',
                    Keys = ["\\lnot", "\\neg", "!"]
                },
            new()
                {
                    Name = "Implication",
                    Code = '→',
                    Keys = ["\\rightarrow", "\\to", "->"]
                },
            new()
                {
                    Name = "Tautology",
                    Code = '⊤',
                    Keys = ["++", "\\top"]
                },
            new()
                {
                    Name = "Contradiction",
                    Code = '⊥',
                    Keys = ["--", "\\bot"]
                },
            new()
            {
                Name = "Conjecture",
                Code = '⊢',
                Keys = ["\\vdash", "\\models", ":="]
            }

            ]);
        private List<Theorem> m_theorems = new List<Theorem>([
            new()
            {
                Name = "Double Negation",
                PatternIn = @"¬¬(A)",
                PatternOut = "A",
                IsEquivalence = true
            },
            new()
            {
                Name = "Negation of Disjunction Elimination",
                PatternIn = @"¬\((A)∨(B)\)",
                PatternOut = "¬A∧¬B",
                IsEquivalence = true
            },
            new()
            {
                Name = "Negation of Conjunction Elimination",
                PatternIn = @"¬\((A)∧(B)\)",
                PatternOut = "¬A∨¬B",
                IsEquivalence = true
            },
            new()
            {
                Name = "Implication Elimination",
                PatternIn = @"\((A)→(B)\)",
                PatternOut = "¬A∨B",
                IsEquivalence = true
            },
            ]);

        private Dictionary<string, Operator> m_Convertors = new Dictionary<string, Operator>();

        public List<char> Symbols { get; } = new();

        public TableauxHelper()
        {
            m_Convertors = m_operators
                .SelectMany(op => op.Keys.Select(key => new { key, op }))
                .ToDictionary(x => x.key, x => x.op);
            Symbols.AddRange(m_codes);
            Symbols.AddRange(m_parentheses);
            Symbols.AddRange(m_operators.Select(op => op.Code));
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="st"></param>
        /// <exception cref="FormatException">Throws if the string contains no premises or conclusion</exception>
        /// <returns></returns>
        public Conjecture Parse(string st)
        {
            foreach (var item in m_Convertors.Keys)
            {
                st.Replace(item, m_Convertors[item].Code.ToString());
            }

            string[] strings = st.Split('⊢');
            Contract.Requires(strings.Length == 2, "The string must contain premises and a conclusion");

            return new Conjecture
            {
                Premises = strings[0].Split(',').ToList(),
                Conclusion = strings[1]
            };
        }

        public TreeNode BuildTree(Conjecture conjecture)
        {

        }

        public bool IsStringLegal(string st) => st.All(Symbols.Contains);

        public bool IsAtomic(string st) => Regex.IsMatch(st, @"[A-Z]") || Regex.IsMatch(st, @"([A-Z])");

        public bool IsAtomicNegation(string st) => Regex.IsMatch(st, @"¬[A-Z]") || Regex.IsMatch(st, @"¬([A-Z])");

        public bool IsLiteral(string st) => IsAtomic(st) || IsAtomicNegation(st);

        public bool IsComplex(string st) => !IsLiteral(st);

        public bool CanSimplify(string st, string pattern) => IsComplex(st) && Regex.IsMatch(st, pattern);
    }
}
