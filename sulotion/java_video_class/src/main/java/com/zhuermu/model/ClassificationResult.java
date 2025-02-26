package com.zhuermu.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import java.util.List;

@Data
public class ClassificationResult {
    @JsonProperty("catetorys")
    private List<Category> categories;
    
    @JsonProperty("tags")
    private List<Tag> tags;
}
