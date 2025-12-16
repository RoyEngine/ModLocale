package second_in_command.skills.misc

import com.fs.starfarer.api.characters.LevelBasedEffect
import com.fs.starfarer.api.characters.MutableCharacterStatsAPI
import com.fs.starfarer.api.characters.SkillSpecAPI
import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc

class InactiveSkill : SCBaseVanillaShipSkill() {
    override fun getScopeDescription(): LevelBasedEffect.ScopeDescription {
        return LevelBasedEffect.ScopeDescription.PILOTED_SHIP
    }

    override fun createCustomDescription(stats: MutableCharacterStatsAPI?, skill: SkillSpecAPI?, info: TooltipMakerAPI?, width: Float) {

        info!!.addPara("该军官由于技能数量超出等级上限导致部分技能失效", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        info!!.addPara("   - 重新指派一名具备 \"军官培训\" 技能的执行军官以恢复其技能。", 0f, Misc.getTextColor(), Misc.getHighlightColor())
    }

    override fun apply(stats: MutableShipStatsAPI?, hullSize: ShipAPI.HullSize?, id: String?, level: Float) {

    }

    override fun unapply(stats: MutableShipStatsAPI?, hullSize: ShipAPI.HullSize?, id: String?) {

    }

}