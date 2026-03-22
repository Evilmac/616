#ifndef IA_TOKENIZER_H
#define IA_TOKENIZER_H

#include <string>
#include <vector>

namespace ia {

// Wrapper ligero sobre HuggingFace Tokenizers C++ API.
// Si HAVE_TOKENIZERS no está definido, esta clase actúa como stub/fallback.
class TokenizerWrapper {
public:
    TokenizerWrapper();
    ~TokenizerWrapper();

    // Cargar tokenizer desde un archivo tokenizer.json exportado por tokenizers/tokenizer
    // Devuelve true si la carga fue exitosa, err contiene mensaje de error en caso contrario.
    bool loadFromFile(const std::string& tokenizer_json_path, std::string& err);

    // Tokenizar: devuelve vector de ids (input_ids) y attention_mask (0/1)
    // Si no está inicializado, devuelve vectores vacíos.
    void encode(const std::string& text, std::vector<int64_t>& input_ids, std::vector<int64_t>& attention_mask, std::string& err) const;

    // Dimensión máxima de tokens que el tokenizer retornará (o 0 si desconocido)
    int maxLength() const;

    bool isReady() const;

private:
    struct Impl;
    Impl* impl_;
};

} // namespace ia

#endif // IA_TOKENIZER_H
