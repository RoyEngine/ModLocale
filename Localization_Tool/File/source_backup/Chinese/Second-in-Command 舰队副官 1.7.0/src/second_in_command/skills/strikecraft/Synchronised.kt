package second_in_command.skills.strikecraft

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class Synchronised : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "玩家"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("你获得直接操控舰队部署的战机的能力", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("   - 要操控战机，将鼠标指向战机的同时按住 CTRL 并{单击右键", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "CTRL", "单击右键")
        tooltip.addPara("   - 不指向另一架战机时按住 CTRL 并{单击右键}以返回操控旗舰", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "CTRL", "单击右键")
        tooltip.addPara("   - 选择操控战机联队的长机能让联队中其他战机自动跟随你", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "")

        tooltip.addSpacer(10f)

        tooltip.addPara("每架战机一次机会，启用直接操控时使其恢复全部弹药，包括导弹", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("   - 恢复后的弹药量可以超过战机的最大载弹量", 0f, Misc.getTextColor(), Misc.getHighlightColor())
        tooltip.addPara("   - 超出上限的弹药将在玩家解除操控时被移除", 0f, Misc.getTextColor(), Misc.getHighlightColor())
        tooltip.addPara("   - 回复的弹药量取决于武器的基础备弹量", 0f, Misc.getTextColor(), Misc.getHighlightColor())

        tooltip.addSpacer(10f)

        tooltip.addPara("你的操舰技能无法对你操控的战机生效，因此战机会获得几种增益: ", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("   - +25%% 伤害抗性", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "+25%")
        tooltip.addPara("   - +30%% 非导弹武器伤害", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "+30%")
        tooltip.addPara("   - +50%% 武器射速", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "+50%")
        tooltip.addPara("   - -50%% 武器产生的幅能", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "50%")
        tooltip.addPara("   - 附近 600 范围内的友军战机获得 1/3 效果的增益", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "600", "1/3")

        tooltip.addSpacer(10f)



    }

    override fun advanceInCombat(data: SCData?, ship: ShipAPI?, amount: Float?) {
        super.advanceInCombat(data, ship, amount)

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {

    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {

    }

    override fun applyEffectsToFighterSpawnedByShip(data: SCData, fighter: ShipAPI?, ship: ShipAPI?, id: String?) {


    }

}